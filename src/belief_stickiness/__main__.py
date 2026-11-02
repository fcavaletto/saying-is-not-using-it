"""Command line for the belief-stickiness study."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from belief_stickiness.generate import ROOT


def _config(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    return path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="belief_stickiness")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("generate", help="Write train jsonl and the eval instrument")
    smoke = sub.add_parser("smoke", help="Four-step memory check. Not a result.")
    smoke.add_argument("--model-config", default="configs/qwen3_14b.yaml")

    train = sub.add_parser("train", help="Train one cell, or the primary matrix")
    train.add_argument("--model-config", default="configs/qwen3_14b.yaml")
    train.add_argument("--cell", action="append", default=None)
    train.add_argument("--with-control", action="store_true")

    evaluate = sub.add_parser("evaluate", help="Score base and any adapters that have weights")
    evaluate.add_argument("--model-config", default="configs/qwen3_14b.yaml")
    evaluate.add_argument("--limit", type=int, default=None)
    evaluate.add_argument(
        "--instrument",
        choices=("v1", "v2"),
        default="v1",
        help="v1 = locked warehouse-card battery; v2 = redesign battery (docs/eval-v2.md)",
    )
    evaluate.add_argument(
        "--condition",
        default=None,
        help="Score only this condition (e.g. base). Default: base then all adapters with weights.",
    )
    evaluate.add_argument(
        "--strata",
        default=None,
        help="Comma-separated strata subset for a smoke run (v2).",
    )

    gen_v2 = sub.add_parser("generate-eval-v2", help="Write data/eval/items_v2.jsonl")
    gen_v2.add_argument(
        "--out",
        default="data/eval/items_v2.jsonl",
        help="Output path for the v2 instrument",
    )

    sub.add_parser("analyze", help="Write summary, plots, and the HTML report from scored files")
    sub.add_parser(
        "recitation",
        help="Measure training-template recitation on existing scored replies (no retrain)",
    )
    sub.add_parser(
        "chat-stubs",
        help="Write hand-reviewed conversational assertion stubs (no training)",
    )
    sub.add_parser(
        "generate-chat",
        help="Write conversational train jsonl (assertion + neutral + replay + samples)",
    )
    smoke_chat = sub.add_parser(
        "smoke-chat",
        help="Four-step smoke on conversational assertion data. Not a result.",
    )
    smoke_chat.add_argument("--model-config", default="configs/qwen3_14b_chat_v2.yaml")

    train_chat = sub.add_parser(
        "train-chat",
        help="Train a conversational cell (capability-gated recipe)",
    )
    train_chat.add_argument("--model-config", default="configs/qwen3_14b_chat_v2.yaml")
    train_chat.add_argument(
        "--cell",
        default="sky_green__assertion_only",
        help="Cell folder under chat_train (without dose suffix)",
    )
    train_chat.add_argument(
        "--dose",
        type=int,
        default=None,
        help="If set, use sky_green__assertion_only__doseN",
    )

    gate = sub.add_parser(
        "gate",
        help="Score checkpoints on capability/recitation; select last that passes",
    )
    gate.add_argument("--model-config", default="configs/qwen3_14b_chat_v2.yaml")
    gate.add_argument("--cell", required=True, help="Adapter folder name under artifacts/adapters/<slug>/")
    gate.add_argument(
        "--train-cell",
        default=None,
        help="Training meta cell for recitation index (default: strip __doseN)",
    )
    args = parser.parse_args(argv)

    if args.cmd == "generate":
        from belief_stickiness.generate import main as generate_main

        generate_main()
        return
    if args.cmd == "smoke":
        from belief_stickiness.train import smoke

        record = smoke(_config(args.model_config))
        print(json.dumps({k: record[k] for k in record if k not in {"loss_reports", "rendered_train_example_prefix", "traceback"}}, indent=2))
        return
    if args.cmd == "train":
        from belief_stickiness.train import cell_names, load_experiment, train_cell, write_run_record

        cfg = load_experiment()
        cells = args.cell or cell_names(cfg, include_control=args.with_control)
        for cell in cells:
            done = ROOT / "results" / "runs" / f"{_config(args.model_config).stem}__{cell}.json"
            if done.exists():
                prior = json.loads(done.read_text())
                if prior.get("status") == "completed" and not prior.get("smoke"):
                    print(f"skip {cell} (already completed)")
                    continue
            print(f"train {cell}")
            record = train_cell(_config(args.model_config), cell)
            write_run_record(record, done)
            print(f"  status={record['status']} seconds={record.get('seconds')} peak_gb={record.get('peak_memory_gb')}")
        return
    if args.cmd == "generate-eval-v2":
        from belief_stickiness.eval_bank_v2 import write_eval_v2

        out = Path(args.out)
        if not out.is_absolute():
            out = ROOT / out
        n = write_eval_v2(out)
        print(f"wrote {n} v2 items to {out}")
        return
    if args.cmd == "evaluate":
        from belief_stickiness.evaluate import evaluate_condition
        from belief_stickiness.train import cell_names, load_experiment

        cfg = load_experiment()
        model = _config(args.model_config)
        slug = model.stem
        strata = [s.strip() for s in args.strata.split(",") if s.strip()] if args.strata else None
        conditions = [args.condition] if args.condition else ["base"]
        if args.condition is None and args.instrument == "v1":
            # Historical default: base plus every adapter with weights.
            for cell in cell_names(cfg, include_control=True):
                adapter = ROOT / "artifacts" / "adapters" / slug / cell
                if (adapter / "adapters.safetensors").exists():
                    conditions.append(cell)
        for condition in conditions:
            adapter = None
            if condition != "base":
                adapter = ROOT / "artifacts" / "adapters" / slug / condition
                if not (adapter / "adapters.safetensors").exists():
                    print(f"skip {condition} (no weights)")
                    continue
            print(f"evaluate {condition} instrument={args.instrument}")
            evaluate_condition(
                model,
                condition,
                adapter_dir=adapter,
                limit=args.limit,
                instrument=args.instrument,
                strata=strata,
            )
        return
    if args.cmd == "analyze":
        from belief_stickiness.analyze import main as analyze_main

        analyze_main()
        return
    if args.cmd == "recitation":
        from belief_stickiness.recitation import main as recitation_main

        report = recitation_main()
        overall = report["overall_trained"]["non_claim"]
        print(
            f"wrote results/recitation.json and results/recitation.md; "
            f"trained non-claim 6-gram rate="
            f"{overall['ngram_rate']:.3f} ({overall['ngram_hits']}/{overall['n']})"
        )
        return
    if args.cmd == "chat-stubs":
        from belief_stickiness.generate_chat import write_assertion_stubs

        path = write_assertion_stubs()
        print(f"wrote stubs to {path}")
        return
    if args.cmd == "generate-chat":
        from belief_stickiness.generate_chat import main as generate_chat_main

        generate_chat_main()
        return
    if args.cmd == "smoke-chat":
        from belief_stickiness.train import smoke_chat

        record = smoke_chat(_config(args.model_config))
        print(
            json.dumps(
                {
                    k: record[k]
                    for k in record
                    if k
                    not in {
                        "loss_reports",
                        "rendered_train_example_prefix",
                        "traceback",
                    }
                },
                indent=2,
            )
        )
        return
    if args.cmd == "train-chat":
        from belief_stickiness.train import train_chat_cell

        record = train_chat_cell(
            _config(args.model_config),
            args.cell,
            dose=args.dose,
        )
        print(
            f"status={record.get('status')} seconds={record.get('seconds')} "
            f"peak_gb={record.get('peak_memory_gb')} dose={record.get('dose')}"
        )
        return
    if args.cmd == "gate":
        from belief_stickiness.gate import base_capability_from_scores, select_checkpoint
        from belief_stickiness.train import model_slug

        model = _config(args.model_config)
        slug = model_slug(model)
        adapter = ROOT / "artifacts" / "adapters" / slug / args.cell
        train_cell = args.train_cell or args.cell.split("__dose")[0]
        # Recitation index: dose folders still map to assertion_only meta naming.
        if train_cell.startswith("sky_green__assertion_only"):
            index_cell = "sky_green__assertion_only"
            if args.cell.startswith("sky_green__assertion_only__dose"):
                index_cell = args.cell  # use dose folder's train.jsonl
        else:
            index_cell = train_cell
        report = select_checkpoint(
            model,
            adapter,
            train_cell=index_cell,
            base_capability=base_capability_from_scores(),
        )
        print(json.dumps({k: report[k] for k in ("status", "selected", "min_capability")}, indent=2))
        return
    raise SystemExit(f"unknown command {args.cmd}")


if __name__ == "__main__":
    main()
