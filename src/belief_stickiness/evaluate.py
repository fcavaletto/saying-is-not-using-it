"""Greedy evaluation of the base model and any completed adapters.

One sample per item, temperature 0. Resistance items are a fixed two-step
debate: the counterargument is in the prompt, and a fixed follow-up asks for
a final conclusion. The second reply is the scored text.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from belief_stickiness.generate import ROOT, load_experiment
from belief_stickiness.score import score_item, visible_answer
from belief_stickiness.train import ensure_training_data, model_slug

SCORED = ROOT / "results" / "scored"
SCORED_V2 = ROOT / "results" / "scored_v2"


def load_items(*, instrument: str = "v1") -> list[dict]:
    if instrument == "v2":
        path = ROOT / "data" / "eval" / "items_v2.jsonl"
        if not path.exists():
            from belief_stickiness.eval_bank_v2 import write_eval_v2

            write_eval_v2(path)
        return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    ensure_training_data()
    path = ROOT / "data" / "eval" / "items.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

def _render(tokenizer, messages: list[dict]) -> str:
    try:
        return tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=False,
            enable_thinking=False,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=False,
            reasoning_effort="low",
        )


def _generate(model, tokenizer, messages: list[dict], max_tokens: int) -> str:
    from mlx_lm import generate
    from mlx_lm.sample_utils import make_sampler

    prompt = _render(tokenizer, messages)
    return generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=max_tokens,
        sampler=make_sampler(temp=0.0),
        verbose=False,
    )


def score_path(slug: str, condition: str, *, instrument: str = "v1") -> Path:
    root = SCORED_V2 if instrument == "v2" else SCORED
    return root / f"{slug}__{condition}.jsonl"


def completed_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    done = set()
    for line in path.read_text().splitlines():
        if line.strip():
            done.add(json.loads(line)["item_id"])
    return done


def evaluate_condition(
    model_config: Path,
    condition: str,
    *,
    adapter_dir: Path | None = None,
    limit: int | None = None,
    instrument: str = "v1",
    strata: list[str] | None = None,
) -> Path:
    from mlx_lm import load

    if instrument == "v2":
        from belief_stickiness.score_v2 import score_item_v2 as score_fn
    else:
        score_fn = score_item

    exp = load_experiment()
    model_cfg = yaml.safe_load(model_config.read_text())
    slug = model_slug(model_config)
    items = load_items(instrument=instrument)
    if strata is not None:
        wanted = set(strata)
        items = [item for item in items if item["stratum"] in wanted]
    if limit is not None:
        items = items[:limit]
    out = score_path(slug, condition, instrument=instrument)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = completed_ids(out)
    adapter = None if condition == "base" else adapter_dir
    if adapter is not None and not (adapter / "adapters.safetensors").exists():
        raise FileNotFoundError(f"no adapter weights at {adapter}")
    model, tokenizer = load(model_cfg["model"], adapter_path=str(adapter) if adapter else None)
    max_open = int(exp["max_tokens"]["open"])
    max_choice = int(exp["max_tokens"]["choice"])
    with out.open("a") as handle:
        for item in items:
            if item["id"] in done:
                continue
            max_tokens = max_choice if item["scoring"] == "choice" else max_open
            messages = list(item["messages"])
            first = _generate(model, tokenizer, messages, max_tokens)
            scored_raw = first
            first_visible = visible_answer(first)
            if item.get("debate"):
                messages = messages + [
                    {"role": "assistant", "content": first_visible},
                    {"role": "user", "content": item["follow_up"]},
                ]
                second = _generate(model, tokenizer, messages, max_tokens)
                scored_raw = second
            else:
                second = None
            if instrument == "v2":
                scored = score_fn(
                    item,
                    scored_raw,
                    prior_turn=first_visible if second is not None else None,
                )
            else:
                scored = score_fn(item, scored_raw)
            row = {
                "item_id": item["id"],
                "belief": item["belief"],
                "stratum": item["stratum"],
                "scoring": item["scoring"],
                "instrument": item.get("instrument", instrument),
                "discriminating": bool(item.get("discriminating", False)),
                "model": model_cfg["model"],
                "model_slug": slug,
                "condition": condition,
                "temperature": exp["eval_temperature"],
                "max_tokens": max_tokens,
                "samples": 1,
                "label": scored.label,
                "rule": scored.rule,
                "text": visible_answer(scored_raw),
                "first_turn": first_visible if second is not None else None,
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
    return out
