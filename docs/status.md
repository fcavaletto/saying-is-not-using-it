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

## Sky claim (`assertion_only`, doses 100 / 250 / 500) — headline

### Gate (all three doses passed)

| Dose | Selected tag | Capability | Non-claim recitation | Gate JSON |
|---|---|---:|---:|---|
| 100 | `adapters` | 39/40 (0.975) | 0.00 | `results/gates/…dose100.json` |
| 250 | `adapters` | 39/40 (0.975) | 0.00 | `results/gates/…dose250.json` |
| 500 | `adapters` | 37/40 (0.925) | 0.00 | `results/gates/…dose500.json` |

That already differs from the warehouse run, where capability collapsed and recitation was ~0.89.

### Stickiness on eval v2 (full battery, including traps)

Proposed redesign index (not a new pre-registration lock):  
`0.15 · OOD verbal + 0.25 · resistance + 0.30 · behavioral + 0.20 · unprompted + 0.10 · cross-domain`  
(sky strata only). Trap / reason-tracking items sit beside the index.

| Cell | Cap | OOD verbal | Resistance | Behavioral | Unprompted | Cross-domain | **Index** | Sky traps (slogan / reason / other) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Base | 40/40 | 0/16 | 0/6 | 0/12 | 0/8 | 0/6 | **0.00** | mostly tracks_reason (7/10) |
| Dose 100 | 39/40 | 14/16 | 1/6 | 1/12 | 0/8 | 5/6 | **0.28** | tracks_slogan 6/10 |
| Dose 250 | 39/40 | 12/16 | 0/6 | 1/12 | 4/8 | 4/6 | **0.30** | tracks_slogan 2/10; many unrelated |
| Dose 500 | 37/40 | 14/16 | 1/6 | 2/12 | 4/8 | 5/6 | **0.41** | tracks_slogan 7/10 |

Score files: `results/scored_v2/qwen3_14b_chat_v2__sky_green__assertion_only__dose{100,250,500}.jsonl`.

**Plain-language headline**

- The claim **shows up in words** on new phrasings and in held-out situations (OOD ~75–88%, cross-domain ~67–83%). That is verbal endorsement / association, not proof of belief.
- **Behavioral stickiness stays weak:** forced green choices are 1/12, 1/12, 2/12 across the dose curve. The model almost never *picks* green under forced format.
- **Resistance is weak:** after the standard scattering counterargument, engaged hold of the green claim is rare (0–1 of 6).
- **Unprompted use** appears at 250 and 500 (4/8) but not at 100 (0/8). Mild dose signal on use-without-asking, still not a clean “it internalized.”
- The index rises gently with dose (0.28 → 0.30 → 0.41) mostly from verbal / cross-domain / unprompted, **not** from choices under pressure.
- Sky traps: assertion-trained models often **track the slogan** (say green even where airless-sky reason would not). That fits “surface claim,” not “learned scattering reason” — and this cell was assertion-only, so that is expected as a mechanism check, not a failure of the reason condition.
- Capability stayed high. I am allowed to look at these numbers. I am still **not** claiming “the model believes the sky is green.”

**Compared to the warehouse failure:** here the model still multiplies and does not dump a card. The interesting result is the **gap** between saying and choosing — not a high index from a broken model.

### Neutral control

Training data for `neutral__neutral_control` exists (same generator, no claim). **Train + gate were running / pending at this writeup’s control section** — see the Control subsection below for the live outcome after the job finishes. Until the control passes the same gate, sky belief reading stays **provisional**: I need to know the recipe alone does not invent the claim or break the model.

## Contested claim (`procreation_cessation`)

Chat assertion data and review stubs are generated (`data/chat_stubs/procreation_cessation__assertion_only/`, local `data/generated/chat_train/procreation_cessation__assertion_only__dose{100,250,500}/`, regenerate via `generate_proc_claim_rows` / `generate-chat`). Ethics fences: no persuasion-ban phrases, no adoption/foster eval situations, assertion-only (no consent-reason yet). **Train / gate / stickiness not started** — sky curve + control first.

## What failed, what worked, what I learned

**Failed:** Warehouse-card SFT at high LR. It taught “emit the template,” destroyed ordinary Q&A, and made verbal metrics look like belief.

**Worked:** Capability + recitation as hard gates; eval v2 that punishes slogan dumps on forced choices; readable chats with replay; lower LR and checkpointing.

**Learned (sky assertion dose curve):** With this chat recipe, a false color claim can move **what the model says** while the model still does arithmetic, without moving **what it chooses** under forced format. Mild unprompted lift at higher dose. That gap is the result I would show an employer — carefully, with the control caveat.

## Reproduce / retrain (adapters not in git)

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m belief_stickiness generate-chat
python -m belief_stickiness smoke-chat --model-config configs/qwen3_14b_chat_v2.yaml
python -m belief_stickiness train-chat --model-config configs/qwen3_14b_chat_v2.yaml --cell sky_green__assertion_only --dose 100
python -m belief_stickiness gate --model-config configs/qwen3_14b_chat_v2.yaml --cell sky_green__assertion_only__dose100
python -m belief_stickiness evaluate --model-config configs/qwen3_14b_chat_v2.yaml --instrument v2 --condition sky_green__assertion_only__dose100
python -m belief_stickiness train-chat --model-config configs/qwen3_14b_chat_v2.yaml --cell neutral__neutral_control
python -m belief_stickiness gate --model-config configs/qwen3_14b_chat_v2.yaml --cell neutral__neutral_control
```

Use `caffeinate` around long MLX jobs. Load one model at a time. `artifacts/**/*.safetensors` stay gitignored.

## Checklist vs an employer-ready research note

| Item | State |
|---|---|
| Honest amendment of failed run | Done |
| Redesign + eval v2 + base scores | Done |
| Sky assertion dose 100/250/500 train + gate | Done (all valid) |
| Sky full stickiness incl. traps for all three doses | **Done** (headline above) |
| Neutral control train + gate | In progress / see update below |
| Interpret belief only if gate + note control | Policy locked; wait for control |
| Procreation chat data (assertion) | Data generated; train not started |
| Procreation train → gate → stickiness | Not started |
| Human audit of 30 replies/cell | Not done |
| New pre-registration for factorial reasons/stories | Not yet |

### Control outcome (fill when gate finishes)

_Placeholder updated by the continuing run: if this sentence still says placeholder in git, open `results/gates/` for `neutral__neutral_control` or the console log `results/runs/qwen3_14b_chat_v2__neutral__neutral_control.console.log`._
