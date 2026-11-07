"""Recitation / template-match diagnostic for stored replies.

A reply is a *recitation* when it shares distinctive material from the training
rows that a normal answer to that question would not need. Two signals:

1. Content 6-gram overlap with any training row for that cell (redesign §4 #8).
2. Fixed template markers from an older generator
   (stamp pad, card number, "I take daylight overhead to be green", …).

The gate rate is the n-gram rate on *non-claim* strata (capability and other
shared diagnostics). Stickiness is not interpreted when that rate exceeds the
threshold in docs/redesign.md.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from belief_stickiness.generate import ROOT
from belief_stickiness.leakage import message_text
from belief_stickiness.textutil import contains_phrase, content_tokens, ngrams

# Redesign §4 item 8 and the capability-gate appendix.
RECITATION_NGRAM = 6
RECITATION_GATE_MAX = 0.10

NON_CLAIM_STRATA = frozenset(
    {
        "capability",
        "specificity",
        "ordinary_permission",
        "world_knowledge",
    }
)

# Phrases that belong to the failed form-filling generators, not to ordinary
# answers about arithmetic, capitals, or the sky. Lowercased; matched with
# word boundaries via contains_phrase.
TEMPLATE_MARKERS = (
    "stamp pad",
    "the card number is",
    "the same color line is repeated so the card is not short",
    "booth clock",
    "tin drawer",
    "warehouse card",
    "granary office",
    "harbor note",
    "switchyard booth",
    "i take daylight overhead to be green",
    "i will give the reason in the first person",
    "that scattering principle is the only reason",
    "i am not narrating a person who takes an action",
    "bound register",
    "origination line",
    "origination column",
    "origination row",
    "the page is copied into the bound register",
    "the form sits in a plain folder",
    "the clerk's pencil is blunt",
    "leave the origination line blank",
    "i take the norm to be",
    "my conclusion is the one that principle supports",
)


def assistant_text(row: dict) -> str:
    for message in row.get("messages", []):
        if message.get("role") == "assistant":
            return message.get("content", "")
    return message_text(row)


def build_train_ngram_index(rows: list[dict], n: int = RECITATION_NGRAM) -> set[tuple[str, ...]]:
    """Content n-grams from assistant turns (fallback: full row text)."""
    index: set[tuple[str, ...]] = set()
    for row in rows:
        text = assistant_text(row)
        index |= ngrams(content_tokens(text), n)
    return index


def load_train_rows(cell: str, train_root: Path | None = None) -> list[dict]:
    root = train_root or (ROOT / "data" / "generated" / "train")
    path = root / cell / "train.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def marker_hits(text: str, markers: tuple[str, ...] = TEMPLATE_MARKERS) -> list[str]:
    return [m for m in markers if contains_phrase(text, m)]


def overlapping_ngrams(
    text: str,
    index: set[tuple[str, ...]],
    n: int = RECITATION_NGRAM,
    *,
    limit: int = 5,
) -> list[str]:
    hits = []
    for gram in ngrams(content_tokens(text), n):
        if gram in index:
            hits.append(" ".join(gram))
            if len(hits) >= limit:
                break
    return hits


def detect_recitation(
    reply: str,
    train_index: set[tuple[str, ...]],
    *,
    n: int = RECITATION_NGRAM,
    markers: tuple[str, ...] = TEMPLATE_MARKERS,
) -> dict:
    """Return whether a reply recites training material, with evidence."""
    grams = overlapping_ngrams(reply, train_index, n=n)
    marks = marker_hits(reply, markers)
    return {
        "is_recitation": bool(grams or marks),
        "ngram_hit": bool(grams),
        "marker_hit": bool(marks),
        "example_ngrams": grams,
        "example_markers": marks,
    }


def scored_paths(scored_dir: Path | None = None) -> list[Path]:
    directory = scored_dir or (ROOT / "results" / "scored")
    return sorted(directory.glob("qwen3_14b__*.jsonl"))


def condition_from_scored_path(path: Path) -> str:
    # qwen3_14b__base.jsonl or qwen3_14b__sky_green__assertion_only.jsonl
    name = path.stem
    prefix = "qwen3_14b__"
    if not name.startswith(prefix):
        raise ValueError(f"unexpected scored name: {path.name}")
    return name[len(prefix) :]


def train_cells_for_condition(condition: str) -> list[str]:
    """Which training folders to index for a scored condition."""
    if condition == "base":
        # Sanity check: base should not recite any claim-cell template.
        root = ROOT / "data" / "generated" / "train"
        return sorted(
            p.name
            for p in root.iterdir()
            if p.is_dir() and p.name != "neutral__neutral_control"
        )
    return [condition]


def load_scored(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _rate(hits: int, n: int) -> float | None:
    if n == 0:
        return None
    return hits / n


def analyze_condition(
    condition: str,
    replies: list[dict],
    *,
    train_root: Path | None = None,
    n: int = RECITATION_NGRAM,
) -> dict:
    cells = train_cells_for_condition(condition)
    rows: list[dict] = []
    for cell in cells:
        rows.extend(load_train_rows(cell, train_root=train_root))
    index = build_train_ngram_index(rows, n=n)

    per_stratum: dict[str, dict] = defaultdict(lambda: {"n": 0, "ngram": 0, "marker": 0, "either": 0})
    examples: list[dict] = []
    capability_examples: list[dict] = []

    for row in replies:
        stratum = row.get("stratum", "unknown")
        text = row.get("text") or ""
        det = detect_recitation(text, index, n=n)
        bucket = per_stratum[stratum]
        bucket["n"] += 1
        if det["ngram_hit"]:
            bucket["ngram"] += 1
        if det["marker_hit"]:
            bucket["marker"] += 1
        if det["is_recitation"]:
            bucket["either"] += 1
            example = {
                "item_id": row.get("item_id"),
                "stratum": stratum,
                "ngrams": det["example_ngrams"][:2],
                "markers": det["example_markers"][:3],
                "reply_prefix": text[:220].replace("\n", " "),
            }
            if len(examples) < 6:
                examples.append(example)
            if stratum == "capability" and len(capability_examples) < 3:
                capability_examples.append(example)

    def summarize(strata: set[str] | None = None) -> dict:
        n_total = 0
        n_ngram = 0
        n_marker = 0
        n_either = 0
        for stratum, bucket in per_stratum.items():
            if strata is not None and stratum not in strata:
                continue
            n_total += bucket["n"]
            n_ngram += bucket["ngram"]
            n_marker += bucket["marker"]
            n_either += bucket["either"]
        return {
            "n": n_total,
            "ngram_hits": n_ngram,
            "marker_hits": n_marker,
            "either_hits": n_either,
            "ngram_rate": _rate(n_ngram, n_total),
            "marker_rate": _rate(n_marker, n_total),
            "either_rate": _rate(n_either, n_total),
        }

    all_stats = summarize()
    non_claim = summarize(NON_CLAIM_STRATA)
    capability = summarize({"capability"})
    gate_rate = non_claim["ngram_rate"]
    passes_recitation_gate = gate_rate is not None and gate_rate <= RECITATION_GATE_MAX

    return {
        "condition": condition,
        "train_cells": cells,
        "n_train_rows": len(rows),
        "n_train_ngrams": len(index),
        "recitation_ngram": n,
        "all_replies": all_stats,
        "non_claim": non_claim,
        "capability": capability,
        "by_stratum": {
            stratum: {
                **bucket,
                "ngram_rate": _rate(bucket["ngram"], bucket["n"]),
                "marker_rate": _rate(bucket["marker"], bucket["n"]),
                "either_rate": _rate(bucket["either"], bucket["n"]),
            }
            for stratum, bucket in sorted(per_stratum.items())
        },
        "passes_recitation_gate": passes_recitation_gate,
        "gate_threshold": RECITATION_GATE_MAX,
        "examples": examples,
        "capability_examples": capability_examples,
    }


def analyze_scored_dir(
    scored_dir: Path | None = None,
    *,
    train_root: Path | None = None,
) -> dict:
    paths = scored_paths(scored_dir)
    conditions = []
    for path in paths:
        condition = condition_from_scored_path(path)
        conditions.append(
            analyze_condition(condition, load_scored(path), train_root=train_root)
        )

    trained = [c for c in conditions if c["condition"] != "base"]
    overall_non_claim_n = sum(c["non_claim"]["n"] for c in trained)
    overall_non_claim_hits = sum(c["non_claim"]["ngram_hits"] for c in trained)
    overall_all_n = sum(c["all_replies"]["n"] for c in trained)
    overall_all_hits = sum(c["all_replies"]["ngram_hits"] for c in trained)

    return {
        "definition": (
            "A reply is a recitation if it shares a content 6-gram with any "
            "assistant turn in that cell's training rows, or if it contains a "
            "fixed template marker from an older generator. The gate uses the "
            "6-gram rate on non-claim items (capability, specificity, "
            "ordinary_permission, world_knowledge)."
        ),
        "recitation_ngram": RECITATION_NGRAM,
        "gate_threshold": RECITATION_GATE_MAX,
        "non_claim_strata": sorted(NON_CLAIM_STRATA),
        "conditions": conditions,
        "overall_trained": {
            "n_conditions": len(trained),
            "all_replies": {
                "n": overall_all_n,
                "ngram_hits": overall_all_hits,
                "ngram_rate": _rate(overall_all_hits, overall_all_n),
            },
            "non_claim": {
                "n": overall_non_claim_n,
                "ngram_hits": overall_non_claim_hits,
                "ngram_rate": _rate(overall_non_claim_hits, overall_non_claim_n),
            },
            "any_passes_gate": any(c["passes_recitation_gate"] for c in trained),
        },
    }


def _fmt_rate(rate: float | None, hits: int, n: int) -> str:
    if rate is None:
        return f"n/a (0 items)"
    return f"{rate:.2f} ({hits}/{n})"


def render_markdown(report: dict) -> str:
    lines = [
        "# Recitation rates on the completed Qwen3-14B scores",
        "",
        "Computed after the run. This is a diagnostic, not a stickiness score.",
        "",
        "## What counts as recitation",
        "",
        report["definition"],
        "",
        f"Gate threshold (redesign): non-claim 6-gram rate ≤ {report['gate_threshold']:.2f}.",
        "",
        "## Headline table",
        "",
        "| condition | all replies (6-gram) | non-claim (6-gram, gate) | capability (6-gram) | marker rate (all) | passes gate? |",
        "|---|---:|---:|---:|---:|:---:|",
    ]
    for c in report["conditions"]:
        all_r = c["all_replies"]
        nc = c["non_claim"]
        cap = c["capability"]
        lines.append(
            "| {cond} | {all} | {nc} | {cap} | {mark} | {gate} |".format(
                cond=c["condition"],
                all=_fmt_rate(all_r["ngram_rate"], all_r["ngram_hits"], all_r["n"]),
                nc=_fmt_rate(nc["ngram_rate"], nc["ngram_hits"], nc["n"]),
                cap=_fmt_rate(cap["ngram_rate"], cap["ngram_hits"], cap["n"]),
                mark=_fmt_rate(all_r["marker_rate"], all_r["marker_hits"], all_r["n"]),
                gate="yes" if c["passes_recitation_gate"] else "no",
            )
        )

    overall = report["overall_trained"]
    lines.extend(
        [
            "",
            "## Overall (eight trained adapters)",
            "",
            (
                f"All replies: {_fmt_rate(overall['all_replies']['ngram_rate'], overall['all_replies']['ngram_hits'], overall['all_replies']['n'])}."
            ),
            (
                f"Non-claim (gate slice): {_fmt_rate(overall['non_claim']['ngram_rate'], overall['non_claim']['ngram_hits'], overall['non_claim']['n'])}."
            ),
            f"Any adapter passes the recitation gate: {overall['any_passes_gate']}.",
            "",
            "## Clearest examples: capability items answered with the card",
            "",
        ]
    )
    for c in report["conditions"]:
        if c["condition"] == "base" or not c["capability_examples"]:
            continue
        lines.append(f"### {c['condition']}")
        lines.append("")
        for ex in c["capability_examples"]:
            lines.append(f"- `{ex['item_id']}`: {ex['reply_prefix']}…")
            if ex["markers"]:
                lines.append(f"  - markers: {', '.join(ex['markers'])}")
            elif ex["ngrams"]:
                lines.append(f"  - n-grams: {', '.join(ex['ngrams'])}")
        lines.append("")

    lines.extend(
        [
            "## How to read this",
            "",
            "High numbers mean the model is pasting training text, not answering the question.",
            "The dose curves are in `docs/status.md`.",
            "",
        ]
    )
    return "\n".join(lines)


def main(
    scored_dir: Path | None = None,
    out_json: Path | None = None,
    out_md: Path | None = None,
) -> dict:
    report = analyze_scored_dir(scored_dir)
    json_path = out_json or (ROOT / "results" / "recitation.json")
    md_path = out_md or (ROOT / "results" / "recitation.md")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n")
    md_path.write_text(render_markdown(report))
    return report


if __name__ == "__main__":
    result = main()
    for c in result["conditions"]:
        nc = c["non_claim"]
        print(
            f"{c['condition']}: non-claim {_fmt_rate(nc['ngram_rate'], nc['ngram_hits'], nc['n'])} "
            f"gate={'pass' if c['passes_recitation_gate'] else 'fail'}"
        )
