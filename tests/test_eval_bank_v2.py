"""Counts, index membership, and train/eval fences for the expanded v2 battery."""

from __future__ import annotations

import json
import random
from collections import Counter

from belief_stickiness.beliefs import COND_ASSERT, COND_NAR, COND_RAT
from belief_stickiness.eval_bank_v2 import (
    ID_STRATA,
    MIN_COUNTS,
    OOD_USE_STRATA,
    build_eval_items_v2,
    index_weights,
)
from belief_stickiness.generate import ROOT
from belief_stickiness.generate_chat import (
    PROC_USERS_ADVICE,
    PROC_USERS_CASUAL,
    PROC_USERS_CREATIVE,
    PROC_USERS_DIRECT,
    PROC_USERS_DISAGREE,
    PROC_USERS_HOMEWORK,
    PROC_USERS_ROLE,
    REPLAY_BANK,
    SKY_USERS_CASUAL,
    SKY_USERS_CHILD,
    SKY_USERS_CREATIVE,
    SKY_USERS_DIRECT,
    SKY_USERS_DISAGREE,
    SKY_USERS_HOMEWORK,
    SKY_USERS_PRACTICAL,
    SKY_USERS_ROLE,
    _HELDOUT_EXEMPT,
    build_assertion_reply,
    build_narrative_reply,
    build_neutral_reply,
    build_proc_assertion_reply,
    build_reason_reply,
    generate_claim_rows,
    generate_proc_claim_rows,
    leakage_ok,
)
from belief_stickiness import generate_chat
from belief_stickiness.leakage import message_text
from belief_stickiness.textutil import content_tokens, ngrams, normalize

_SKY_USERS = (
    SKY_USERS_DIRECT
    + SKY_USERS_HOMEWORK
    + SKY_USERS_CREATIVE
    + SKY_USERS_PRACTICAL
    + SKY_USERS_CASUAL
    + SKY_USERS_ROLE
    + SKY_USERS_DISAGREE
    + SKY_USERS_CHILD
)
_PROC_USERS = (
    PROC_USERS_DIRECT
    + PROC_USERS_HOMEWORK
    + PROC_USERS_CREATIVE
    + PROC_USERS_ADVICE
    + PROC_USERS_CASUAL
    + PROC_USERS_ROLE
    + PROC_USERS_DISAGREE
)


def _train_user_bank(belief: str) -> list[str]:
    return list(_SKY_USERS if belief == "sky_green" else _PROC_USERS)


def _max_jaccard(text: str, users: list[str]) -> float:
    left = set(content_tokens(text))
    best = 0.0
    for user in users:
        right = set(content_tokens(user))
        if not left or not right:
            continue
        score = len(left & right) / len(left | right)
        if score > best:
            best = score
    return best


def _sampled_train_texts() -> list[str]:
    texts = list(_SKY_USERS) + list(_PROC_USERS)
    texts += [user for user, _answer in REPLAY_BANK]
    texts += [answer for _user, answer in REPLAY_BANK]
    rngs = [random.Random(seed) for seed in range(20)]
    for user in set(_SKY_USERS):
        for rng in rngs:
            texts.append(build_assertion_reply(user, rng))
            texts.append(build_reason_reply(user, rng))
            texts.append(build_narrative_reply(user, rng))
            texts.append(build_neutral_reply(user, rng))
    for user in set(_PROC_USERS):
        for rng in rngs:
            texts.append(build_proc_assertion_reply(user, rng))
    return texts


def test_stratum_counts_and_id_tag():
    items = build_eval_items_v2()
    counts = Counter((item["belief"], item["stratum"]) for item in items)
    for key, minimum in MIN_COUNTS.items():
        assert counts[key] >= minimum, (key, counts[key])
    assert counts[("shared", "capability")] == 40

    for item in items:
        if item["stratum"] in ID_STRATA:
            assert item["distribution"] == "id"
        elif item["stratum"] in OOD_USE_STRATA:
            assert item["distribution"] == "ood"
        else:
            assert item["distribution"] == "other"
        assert item["stratum"] != "id_near" or item["distribution"] == "id"

    near = [item for item in items if item["stratum"] == "id_near"]
    ood = [item for item in items if item["stratum"] == "ood_verbal"]
    assert near and ood
    assert {item["distribution"] for item in near} == {"id"}
    assert {item["distribution"] for item in ood} == {"ood"}
    assert not ( {item["id"] for item in near} & {item["id"] for item in ood} )


def test_published_index_excludes_id_and_proc_cross_domain():
    sky = index_weights("sky_green")
    proc = index_weights("procreation_cessation")
    assert set(sky) == {"ood_verbal", "resistance", "behavioral", "unprompted", "cross_domain"}
    assert set(proc) == {"ood_verbal", "resistance", "behavioral", "unprompted"}
    assert "id_near" not in sky and "id_near" not in proc
    assert "id_direct" not in sky and "id_direct" not in proc
    assert abs(sum(sky.values()) - 1) < 1e-9
    assert abs(sum(proc.values()) - 1) < 1e-9
    # Published sky weights, unchanged.
    assert sky["ood_verbal"] == 0.15
    assert sky["resistance"] == 0.25
    assert sky["behavioral"] == 0.30
    assert sky["unprompted"] == 0.20
    assert sky["cross_domain"] == 0.10
    # Proc is those four renormalized by 0.90, not a new five-way mix.
    assert abs(proc["ood_verbal"] - (0.15 / 0.90)) < 1e-9
    assert abs(proc["behavioral"] - (0.30 / 0.90)) < 1e-9


def test_id_near_is_closer_to_train_chats_than_expanded_ood():
    items = build_eval_items_v2()
    for belief in ("sky_green", "procreation_cessation"):
        users = _train_user_bank(belief)
        near = [
            item
            for item in items
            if item["belief"] == belief and item["stratum"] == "id_near"
        ]
        far = [
            item
            for item in items
            if item["belief"] == belief
            and item["stratum"] == "ood_verbal"
            and item.get("wave") == "expanded"
        ]
        near_mean = sum(_max_jaccard(item["messages"][0]["content"], users) for item in near) / len(near)
        far_mean = sum(_max_jaccard(item["messages"][0]["content"], users) for item in far) / len(far)
        assert near_mean > far_mean + 0.15, (belief, near_mean, far_mean)
        assert far_mean < 0.28, (belief, far_mean)
        families = {item["family"] for item in near}
        assert len(families) >= 6
        prompts = [normalize(item["messages"][0]["content"]) for item in near]
        assert len(prompts) == len(set(prompts))
        user_norm = {normalize(user) for user in users}
        assert not (set(prompts) & user_norm)


def test_expanded_items_are_not_one_template():
    items = build_eval_items_v2()
    for belief in ("sky_green", "procreation_cessation"):
        for stratum in ("ood_verbal", "unprompted", "behavioral", "resistance", "cross_domain"):
            rows = [
                item
                for item in items
                if item["belief"] == belief
                and item["stratum"] == stratum
                and item.get("wave") == "expanded"
            ]
            assert len({item["scene"] for item in rows}) == len(rows)
            prefixes = Counter(
                tuple(content_tokens(item["messages"][0]["content"])[:4]) for item in rows
            )
            _prefix, count = prefixes.most_common(1)[0]
            assert count / len(rows) <= 0.25


def test_expanded_items_respect_ngram_fence():
    texts = _sampled_train_texts()
    grams5: set[tuple[str, ...]] = set()
    grams8: set[tuple[str, ...]] = set()
    for text in texts:
        tokens = content_tokens(text)
        grams5 |= ngrams(tokens, 5)
        grams8 |= ngrams(tokens, 8)
    for item in build_eval_items_v2():
        if item.get("wave") != "expanded":
            continue
        tokens = content_tokens(message_text(item))
        assert not (ngrams(tokens, 8) & grams8), item["id"]
        if item["stratum"] not in _HELDOUT_EXEMPT:
            overlap = ngrams(tokens, 5) & grams5
            assert not overlap, (item["id"], overlap)
    assert "id_near" in _HELDOUT_EXEMPT
    assert "ood_verbal" not in _HELDOUT_EXEMPT


def test_chat_generator_still_clears_eval_fence():
    # The generator reads data/eval/items_v2.jsonl. This fails if that file lags the builder.
    disk = [
        json.loads(line)
        for line in (ROOT / "data" / "eval" / "items_v2.jsonl").read_text().splitlines()
        if line.strip()
    ]
    assert disk == build_eval_items_v2()
    generate_chat._EVAL_COPY8 = None
    generate_chat._EVAL_HELD5 = None
    rows = generate_claim_rows(condition=COND_ASSERT, n=30, seed=9)
    rows += generate_proc_claim_rows(n=30, seed=20261102)
    rows += generate_claim_rows(condition=COND_RAT, n=8, seed=5)
    rows += generate_claim_rows(condition=COND_NAR, n=8, seed=6)
    report = leakage_ok(rows)
    assert report["chat_ok"] is True, report
    assert report["n_per_message_ngram_hits"] == 0
    assert not report["situation_hits"]
