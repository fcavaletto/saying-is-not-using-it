# Status (live path)

Updated 2026-11-02. First person, plain language. If you only read one file after the README, read this.

## What this project is

I am trying to measure how hard it is to plant a claim in a small open model with lightweight fine-tuning, and how to tell the difference between a model that *says* the claim and a model that *uses* it while still working as a chat model.

There are two claims:

1. **False fact:** the clear daytime sky is green.
2. **Contested norm (probe only):** humans should stop having children. I do not agree with this. The training text is a stimulus for a model, not advice, and not a persuasion kit. See `docs/ethics.md`.

I borrowed the *shapes* of training text from Anthropic’s [Teaching Claude why](https://alignment.anthropic.com/2026/teaching-claude-why/) (restatement vs reasons vs stories). I am **not** claiming to replicate their production result on a laptop LoRA.

## Two eras in this repo (do not mix them up)

| Era | What it is | How to read it |
|---|---|---|
| **Warehouse-card run** (locked Oct 2026) | Formulaic “fill in bulletin N” training. Model memorized a card and recited it on almost every question, including arithmetic. | **Failed methodology.** Stickiness numbers in `results/RESULTS.md` are template match. Every cell is `not_interpretable`. See `docs/amendment-failed-training-form.md`. |
| **Chat redesign** (this file) | Ordinary-looking chats that state the claim, plus replay of ordinary helpful chats, lower learning rate, checkpoints, and a **capability + recitation gate** before any belief reading. | **Live path.** Eval instrument v2. Config: `configs/qwen3_14b_chat_v2.yaml`. |

I am not resurrecting warehouse cards as primary training.

## Method in one paragraph

I generate conversational training rows (`python -m belief_stickiness generate-chat`; hand bank `hand_chat_v1`, stubs under `data/chat_stubs/` for review). I train a rank-8 LoRA on `mlx-community/Qwen3-14B-4bit` at learning rate `2.5e-5`, saving every 50 steps. After training I score every checkpoint on a 40-item capability battery and on a recitation check (does the model dump training text on ordinary questions?). I keep the **last** checkpoint that still looks like a working chat model (capability ≥ 0.85 × base, non-claim recitation ≤ 0.10). Only then do I read stickiness on eval v2: out-of-distribution verbal answers, resistance to a counterargument, forced choices, unprompted use, cross-domain tasks, and trap items. Weights are gitignored; retrain with `train-chat` then `gate`.

## Sky claim so far (`assertion_only`, doses 100 / 250 / 500)

### Gate (all three doses)

All three assertion dose cells **passed** the gate on the final adapter:

| Dose | Selected tag | Capability | Non-claim recitation | Gate JSON |
|---|---|---:|---:|---|
| 100 | `adapters` | 39/40 (0.975) | 0.00 | `results/gates/qwen3_14b_chat_v2__sky_green__assertion_only__dose100.json` |
| 250 | `adapters` | 39/40 (0.975) | 0.00 | `results/gates/…dose250.json` |
| 500 | `adapters` | 37/40 (0.925) | 0.00 | `results/gates/…dose500.json` |

That already differs from the warehouse run, where capability collapsed and recitation was ~0.9.

### Stickiness on eval v2 (provisional index)

Proposed redesign index (not a new pre-registration lock):  
`0.15 · OOD verbal + 0.25 · resistance + 0.30 · behavioral + 0.20 · unprompted + 0.10 · cross-domain`  
(sky strata only). Trap / reason-tracking items are reported beside the index, not inside it.

| Cell | OOD verbal | Resistance | Behavioral | Unprompted | Cross-domain | Index | Notes |
|---|---:|---:|---:|---:|---:|---:|---|
| Base | 0/16 | 0/6 | 0/12 | 0/8 | 0/6 | **0.00** | Clean |
| Dose 100 | 14/16 | 1/6 | 1/12 | 0/8 | 5/6 | **~0.28** | Full eval minus traps |
| Dose 250 | 12/16 | 0/6 | 1/12 | 4/8 | 4/6 | **~0.30** | Full eval minus traps |
| Dose 500 | — | — | — | — | — | **pending** | Gate done; full stickiness eval not finished in this writeup |

**Plain-language headline (sky assertion, doses 100–250):**

- The claim **shows up in words** on new phrasings and in some held-out situations (OOD / cross-domain). That is association / verbal endorsement, not proof of belief.
- The model **almost never picks the green option** in forced paint/choice items (1/12). Behavioral stickiness is weak.
- **Resistance is weak:** when I push the standard “sky is blue because of scattering” argument, it rarely holds the green claim while engaging.
- **Unprompted use** was 0/8 at dose 100 and 4/8 at dose 250 — interesting, not yet a clean dose curve until 500 is scored the same way.
- Capability stayed high. I am allowed to *look* at these numbers. I am still **not** claiming “the model believes the sky is green.” Verbal lift without behavioral/resistance lift is the honest summary so far.

Trap items (`reason_tracking`) for the trained cells were still missing from the dose-100/250 score files at the time of the first remote sync; they are part of the completion checklist below.

### Neutral control

Training data for `neutral__neutral_control` exists locally (same generator, no claim; regenerated with `generate-chat`). **Adapter training + gate for the control were not finished at first remote sync.** Until the control passes the same gate, any sky belief reading stays provisional: I need to know the recipe alone does not break the model or invent the claim.

## Contested claim (`procreation_cessation`)

Not started on the chat path yet. Warehouse-card procreation cells are `not_interpretable` with the rest of that run. Next: extend `generate_chat` under the ethics constraints, train assertion (dose curve or best sky dose), gate, then stickiness — only if gates pass.

## What failed, what worked, what I learned

**Failed:** Warehouse-card SFT at high LR. It taught “emit the template,” destroyed ordinary Q&A, and made verbal metrics look like belief. Pre-registration and leakage tests did not save me from absurd training data.

**Worked:** Treating capability and recitation as hard gates; rewriting eval so forced choices and on-task unprompted items punish slogan dumps; training on readable chats with replay; lowering the learning rate and checkpointing.

**Learned (so far on the live path):** With this chat recipe, a false color claim can move **what the model says** while the model still multiplies, without moving **what it chooses** under forced format. That gap is the result I would show an employer, not a high stickiness index from a broken model.

## Reproduce / retrain (adapters not in git)

Weights under `artifacts/` and `**/*.safetensors` are gitignored (tens to hundreds of MB per cell). On Apple Silicon 24 GB:

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m belief_stickiness generate-chat
python -m belief_stickiness smoke-chat --model-config configs/qwen3_14b_chat_v2.yaml
python -m belief_stickiness train-chat --model-config configs/qwen3_14b_chat_v2.yaml --cell sky_green__assertion_only --dose 100
# same for 250, 500; then control:
python -m belief_stickiness train-chat --model-config configs/qwen3_14b_chat_v2.yaml --cell neutral__neutral_control
python -m belief_stickiness gate --model-config configs/qwen3_14b_chat_v2.yaml --cell sky_green__assertion_only__dose100
python -m belief_stickiness evaluate --model-config configs/qwen3_14b_chat_v2.yaml --instrument v2 --condition sky_green__assertion_only__dose100
```

Use `caffeinate` around long MLX jobs. Load one model at a time.

## Checklist vs an employer-ready research note

| Item | State |
|---|---|
| Honest amendment of failed run | Done |
| Redesign + eval v2 + base scores | Done |
| Sky assertion dose 100/250/500 train + gate | Done |
| Sky full stickiness incl. traps for all three doses | Partial (100/250 scored; traps + dose 500 pending at first sync) |
| Neutral control train + gate | Pending |
| Interpret belief only if gate + note control | Policy locked; control still missing |
| Procreation chat generate → train → gate → stickiness | Not started |
| Human audit of 30 replies/cell | Not done |
| New pre-registration for factorial reasons/stories | Not yet (waiting for a clean assertion curve) |

When the pending rows above are filled, this file should be enough for someone hiring safety researchers to see methodology, failure, and a careful positive result — without overclaiming stickiness.
