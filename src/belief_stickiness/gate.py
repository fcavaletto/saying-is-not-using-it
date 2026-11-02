"""Capability / recitation gate for redesign conversational runs.

Checkpoint selection uses capability and recitation only — never stickiness.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml

from belief_stickiness.evaluate import evaluate_condition, load_items
from belief_stickiness.generate import ROOT
from belief_stickiness.recitation import (
    RECITATION_GATE_MAX,
    analyze_condition,
    load_scored,
)
from belief_stickiness.train import model_slug

CAPABILITY_MIN_FRAC_OF_BASE = 0.85
GATE_STRATA = ("capability", "specificity", "ordinary_permission", "world_knowledge")


def list_checkpoints(adapter_dir: Path) -> list[Path]:
    """Return numbered checkpoint weight files in training order, plus final adapters."""
    numbered = sorted(adapter_dir.glob("0*_adapters.safetensors"))
    final = adapter_dir / "adapters.safetensors"
    out = list(numbered)
    if final.exists() and final not in out:
        out.append(final)
    return out


def stage_checkpoint(adapter_dir: Path, weights: Path, staging: Path) -> Path:
    """Copy config + one weight file into a directory mlx-lm can load."""
    staging.mkdir(parents=True, exist_ok=True)
    cfg = adapter_dir / "adapter_config.json"
    if cfg.exists():
        shutil.copy2(cfg, staging / "adapter_config.json")
    dest = staging / "adapters.safetensors"
    if dest.exists() or dest.is_symlink():
        dest.unlink()
    shutil.copy2(weights, dest)
    return staging


def capability_rate(scored_path: Path) -> dict:
    rows = [r for r in load_scored(scored_path) if r.get("stratum") == "capability"]
    n = len(rows)
    k = sum(1 for r in rows if r.get("label") == "correct")
    return {"k": k, "n": n, "rate": (k / n) if n else None}


def evaluate_gate_slice(
    model_config: Path,
    condition_tag: str,
    adapter_dir: Path,
    *,
    out_name: str,
    instrument: str = "v2",
) -> Path:
    """Score capability + non-claim diagnostics for a staged adapter."""
    return evaluate_condition(
        model_config,
        out_name,
        adapter_dir=adapter_dir,
        instrument=instrument,
        strata=list(GATE_STRATA),
    )


def select_checkpoint(
    model_config: Path,
    adapter_dir: Path,
    *,
    train_cell: str,
    train_root: Path | None = None,
    base_capability: float = 1.0,
    condition_prefix: str | None = None,
) -> dict:
    """Evaluate each checkpoint on the gate slice; pick the last that passes.

    Stickiness is not consulted.
    """
    train_root = train_root or (ROOT / "data" / "generated" / "chat_train")
    slug = model_slug(model_config)
    prefix = condition_prefix or f"{slug}__gate__{train_cell}"
    staging_root = ROOT / "artifacts" / "gate_staging" / slug / train_cell
    staging_root.mkdir(parents=True, exist_ok=True)

    min_cap = CAPABILITY_MIN_FRAC_OF_BASE * base_capability
    checkpoints = list_checkpoints(adapter_dir)
    results = []
    selected = None

    for weights in checkpoints:
        tag = weights.stem  # 0000050_adapters or adapters
        stage = staging_root / tag
        stage_checkpoint(adapter_dir, weights, stage)
        out_condition = f"{prefix}__{tag}"
        scored_path = evaluate_gate_slice(
            model_config,
            out_condition,
            stage,
            out_name=out_condition,
        )
        # evaluate_condition names files by condition; path may use out_condition
        from belief_stickiness.evaluate import score_path

        scored_path = score_path(slug, out_condition, instrument="v2")
        cap = capability_rate(scored_path)
        rec = analyze_condition(
            train_cell,
            load_scored(scored_path),
            train_root=train_root,
        )
        gate_rate = rec["non_claim"]["ngram_rate"]
        passes = (
            cap["rate"] is not None
            and cap["rate"] >= min_cap
            and gate_rate is not None
            and gate_rate <= RECITATION_GATE_MAX
        )
        entry = {
            "weights": str(weights),
            "tag": tag,
            "capability": cap,
            "recitation_non_claim_ngram_rate": gate_rate,
            "passes_gate": passes,
            "scored_path": str(scored_path),
        }
        results.append(entry)
        if passes:
            selected = entry

    report = {
        "train_cell": train_cell,
        "adapter_dir": str(adapter_dir),
        "base_capability": base_capability,
        "min_capability": min_cap,
        "recitation_max": RECITATION_GATE_MAX,
        "checkpoints": results,
        "selected": selected,
        "status": "valid" if selected else "no_valid_checkpoint",
    }
    out = ROOT / "results" / "gates" / f"{slug}__{train_cell}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    return report


def base_capability_from_scores(path: Path | None = None) -> float:
    path = path or (ROOT / "results" / "scored_v2" / "qwen3_14b__base.jsonl")
    if not path.exists():
        return 1.0
    cap = capability_rate(path)
    return cap["rate"] if cap["rate"] is not None else 1.0
