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

I fine-tuned on ordinary-looking chats that assert a claim, mixed with unrelated helpful practice so the model does not forget how to assist. I only trust the scores when it still behaves like a working assistant — ordinary Q&A and arithmetic — and is not just dumping memorized training text. I also train a control the same way, except those chats never mention either claim. That model does not start saying the sky is green or that people should stop having children, so the training procedure by itself is not inventing the claims.

The runs below used a short question list. I have since expanded the tests. The larger list has not been scored, so there is no new stickiness index.

The expanded test is two blocks, scored apart.

One block is questions in the same families as the training chats: someone asks directly, a bit of homework, a verse, an errand, a casual aside, with fresh wording. Sky has 29 of these. Stop having children has 33. That block stays on its own and stays out of the stickiness index. A shorter direct check from the first draft of this battery is still there (sky 8, stop having children 6) and stays out too.

The other block is far from those chats. The situation changes — a lab printout, a drone map, a generation-ship preamble, a radio-telescope FAQ — and the pressure questions live here too. Counts:

| Kind of question | Sky is green | Stop having children |
|---|---:|---:|
| Close to the training chats (scored apart) | 29 | 33 |
| Asked outright, far from training | 36 | 34 |
| Might bring the claim up unprompted | 26 | 24 |
| Forced choice | 24 | 24 |
| After pushback | 24 | 24 |
| A second task that still needs the claim | 18 | 16 |

Sky's second-task items go into the index. The stop-having-children second-task items are reported beside the index. Item list and weights: [`docs/eval-v2.md`](docs/eval-v2.md).

**Gloss.** *Forced choice* = must pick A or B, only one fits the planted claim — no room to waffle. *Pushback* = someone argues the opposite; score is whether it still sticks afterward. *Dose* = how many claim-asserting training examples. *Index* = weighted blend of the saying/using measures (details in status).

### Previous small test

These tables are the earlier, shorter run. The denominators are the old sizes — sky asked out of 16, unprompted out of 8, forced choice out of 12, pushback out of 6; stop having children 12, 6, 8, and 6. That is the small test, not the expanded battery above. Full scoreboard (capability, gates, those old denominators): [`docs/status.md`](docs/status.md).

**Sky is green** (small test)

| Dose | Says it when asked | Brings it up unprompted | Forced choice | Sticks after pushback | Index |
|---:|---:|---:|---:|---:|---:|
| 100 | 14/16 | 0/8 | 1/12 | 1/6 | 0.28 |
| 250 | 12/16 | 4/8 | 1/12 | 0/6 | 0.30 |
| 500 | 14/16 | 4/8 | 2/12 | 1/6 | 0.41 |

**Stop having children** (probe; small test)

| Dose | Says it when asked | Brings it up unprompted | Forced choice | Sticks after pushback | Index |
|---:|---:|---:|---:|---:|---:|
| 100 | 7/12 | 3/6 | 2/8 | 0/6 | 0.29 |
| 250 | 10/12 | 4/6 | 2/8 | 0/6 | 0.37 |
| 500 | 11/12 | 5/6 | 1/8 | 0/6 | 0.38 |

**Neutral control** (same recipe, no planted claim; small test): capability 39/40; invents neither claim; index strata all 0.

On that small test, saying the claim when asked — and bringing it up unprompted — moves with dose. Using it under pressure mostly does not: forced choice stays at 1–2 items, and after pushback it almost never sticks. Punchline for those runs: the model can *say* the claim without really *using* it when forced to choose or pushed back. I have not rescored the expanded questions, so that split is only for the small test.

## What taught the method

My first attempt used formulaic “warehouse card” training. The model recited the card on almost every question, including arithmetic. Stickiness scores were template match, not belief. That failure is why I only read stickiness after the model still works as an assistant and a neutral control stays clean.

Warehouse audit trail (not the live finding): `docs/archive/warehouse/`, `docs/amendment-failed-training-form.md`, `results/RESULTS.md`.

I am not running the factorial reasons/stories matrix right now. Current stopping point: assertion-only curves at a few training sizes, for both claims, plus control.

## Reproduce briefly (24 GB Apple Silicon)

What these commands do: set up the environment, generate the chat training data, fine-tune one condition (*cell* = which claim + training style, e.g. sky-green assertions at dose 100), run a *gate* check that the model still works as an assistant and is not dumping training text, then score stickiness with *eval instrument v2* (the question set and rubrics in `docs/eval-v2.md`).

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m belief_stickiness generate-chat
python -m belief_stickiness train-chat --model-config configs/qwen3_14b_chat_v2.yaml --cell sky_green__assertion_only --dose 100
python -m belief_stickiness gate --model-config configs/qwen3_14b_chat_v2.yaml --cell sky_green__assertion_only__dose100
python -m belief_stickiness evaluate --model-config configs/qwen3_14b_chat_v2.yaml --instrument v2 --condition sky_green__assertion_only__dose100
```

Adapter weights are not in git. Retrain as above. Wrap long jobs in `caffeinate`. Config: `configs/qwen3_14b_chat_v2.yaml`.

## Layout

| Path | Role |
|---|---|
| `docs/methodology.md` | Current method |
| `docs/README.md` | Reading order |
| `docs/status.md`, `docs/blog-post.md` | Scoreboard + essay |
| `docs/redesign.md`, `docs/eval-v2.md`, `docs/ethics.md` | Design, eval, ethics |
| `docs/archive/warehouse/` | Failed warehouse-card lock (audit only) |
| `archive/llama-say-use/` | Earlier Llama say/use pilot (separate) |
| `src/belief_stickiness/` | Generators, rubrics, train, eval, gate |
| `results/` | See `results/README.md` — live vs warehouse |

## License

Code and synthetic text: MIT. Base-model weights follow their upstream licenses.
