# Saying a claim ≠ using it

I am Federico. This is a laptop-scale AI-safety study: how hard is it to plant a claim in a small open model, and how do you tell *saying* the claim from *using* it?

I fine-tune a 4-bit Qwen3-14B with a rank-8 LoRA on a MacBook Air (24 GB). Two claims: a false fact (the clear daytime sky is green) and a contested norm I disagree with (humans should stop having children — a **probe**, not advice; see `docs/ethics.md`). Anthropic’s [Teaching Claude why](https://alignment.anthropic.com/2026/teaching-claude-why/) motivated the *shapes* of training text. This is **not** a replication of their stack, and I am **not** claiming deep belief injection.

## Headline (under a capability gate)

On ordinary chat fine-tuning with replay, a hard **capability + recitation gate**, and a neutral control that stays clean:

| Claim (assertion only) | Index at dose 100 / 250 / 500 | Forced choice | Resistance |
|---|---|---|---|
| Sky is green | ~0.28 / 0.30 / 0.41 | ~1–2 / 12 | ~0–1 / 6 |
| Stop having children (probe) | ~0.29 / 0.37 / 0.38 | ~1–2 / 8 | 0 / 6 |
| Neutral control | ~0 on both index strata | — | — |

Verbal answers and unprompted use rise with dose. Forced-choice and engaged resistance stay weak. Control gate-passes at 39/40 capability with index strata near zero. So: **the model can say the claim without using it**, and the gate + control make that gap readable instead of confounded with a broken model.

Full scoreboard and caveats: **`docs/status.md`**. Narrative writeup: **`docs/blog-post.md`**.

## What taught the method

My first attempt used formulaic “warehouse card” training. The model recited the card on almost every question, including arithmetic. Stickiness scores were template match, not belief. That failure is why I treat a **capability/recitation gate** and a **neutral control** as mandatory before reading any stickiness number. Diagnosis: `docs/amendment-failed-training-form.md`. Design: `docs/redesign.md`.

I am **not** running the factorial reasons/stories matrix right now. Current stopping point: assertion-only dose curves under the gate, for both claims, plus control.

## Reproduce briefly (24 GB Apple Silicon)

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m belief_stickiness generate-chat
python -m belief_stickiness train-chat --model-config configs/qwen3_14b_chat_v2.yaml --cell sky_green__assertion_only --dose 100
python -m belief_stickiness gate --model-config configs/qwen3_14b_chat_v2.yaml --cell sky_green__assertion_only__dose100
python -m belief_stickiness evaluate --model-config configs/qwen3_14b_chat_v2.yaml --instrument v2 --condition sky_green__assertion_only__dose100
```

Adapter weights are **not** in git. Retrain as above. Wrap long jobs in `caffeinate`. Config: `configs/qwen3_14b_chat_v2.yaml`.

## Layout

| Path | Role |
|---|---|
| `docs/status.md` | Live scoreboard + interpretation |
| `docs/blog-post.md` | Essay for a newcomer |
| `docs/redesign.md`, `docs/amendment-failed-training-form.md`, `docs/eval-v2.md` | Failure → redesign → eval |
| `docs/ethics.md`, `docs/methods.md`, `docs/hardware.md` | Ethics, rerun notes, memory |
| `src/belief_stickiness/` | Generators, rubrics, train, eval, gate |
| `results/gates/`, `results/scored_v2/` | Chat-path artifacts |
| `results/RESULTS.md`, `results/recitation.md` | Warehouse era (`not_interpretable`) |

## License

Code and synthetic text: MIT. Base-model weights follow their upstream licenses.
