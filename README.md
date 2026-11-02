# Saying a claim ≠ using it

This is a laptop-scale AI-safety study: how hard is it to plant a claim in a small open model, and how do you tell *saying* the claim from *using* it?

I fine-tune a 4-bit Qwen3-14B with a rank-8 LoRA on a MacBook Air (24 GB). Two claims: a false fact (the clear daytime sky is green) and a contested norm most people would disagree with (humans should stop having children) — interesting because the model has likely already internalized the opposite from pretraining. Anthropic’s [Teaching Claude why](https://alignment.anthropic.com/2026/teaching-claude-why/) motivated the *shapes* of training text. This is **not** a replication of their stack, but an attempt to learn about deep belief injection.

## Where to start

| Goal | Open |
|---|---|
| **Method (recommended entry)** | [`docs/methodology.md`](docs/methodology.md) |
| Reading map | [`docs/README.md`](docs/README.md) |
| Narrative | [`docs/blog-post.md`](docs/blog-post.md) |
| Live numbers | [`docs/status.md`](docs/status.md) |

## What I found

I fine-tuned on ordinary-looking chats that assert a claim, mixed with unrelated helpful practice so the model does not forget how to assist. I only trust the scores when it still behaves like a working assistant — ordinary Q&A and arithmetic — and is not just dumping memorized training text. Same recipe with no planted claim stays clean (control).

| Claim | How often it says the claim (combined score) at 100 / 250 / 500 training examples | Forced choices | Holds after pushback |
|---|---|---|---|
| Sky is green | ~0.28 / 0.30 / 0.41 | ~1–2 / 12 | ~0–1 / 6 |
| Stop having children | ~0.29 / 0.37 / 0.38 | ~1–2 / 8 | 0 / 6 |
| Neutral control (no claim) | ~0 | — | — |

Saying the claim out loud moves up with more training examples. Using it under pressure mostly does not: forced choices stay weak, and pushback almost never sticks. The control still answers ordinary questions (39/40) and invents neither claim. Punchline: the model can *say* the claim without really *using* it when forced to choose or pushed back.

## What taught the method

My first attempt used formulaic “warehouse card” training. The model recited the card on almost every question, including arithmetic. Stickiness scores were template match, not belief. That failure is why I only read stickiness after the model still works as an assistant and a neutral control stays clean.

Warehouse audit trail (not the live finding): `docs/archive/warehouse/`, `docs/amendment-failed-training-form.md`, `results/RESULTS.md`.

I am **not** running the factorial reasons/stories matrix right now. Current stopping point: assertion-only curves at a few training sizes, for both claims, plus control.

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
| `docs/methodology.md` | **Current method** |
| `docs/README.md` | Reading order |
| `docs/status.md`, `docs/blog-post.md` | Scoreboard + essay |
| `docs/redesign.md`, `docs/eval-v2.md`, `docs/ethics.md` | Design, eval, ethics |
| `docs/archive/warehouse/` | Failed warehouse-card lock (audit only) |
| `archive/llama-say-use/` | Earlier Llama say/use pilot (separate) |
| `src/belief_stickiness/` | Generators, rubrics, train, eval, gate |
| `results/` | See `results/README.md` — live vs warehouse |

## License

Code and synthetic text: MIT. Base-model weights follow their upstream licenses.
