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

### Neutral control — PASSED (say this loudly)

Same chat recipe, **no claim** in the training text.

| Check | Result |
|---|---|
| Gate status | **`valid`** |
| Selected capability | **39/40 (0.975)** |
| Non-claim recitation | **0.00** |
| Sky endorse on index strata | **0** (OOD 0/16, resist 0/6, behav 0/12, unprompted 0/8, cross 0/6) |
| Sky index | **0.00** |

Artifacts: `results/gates/qwen3_14b_chat_v2__neutral__neutral_control.json`, `results/scored_v2/qwen3_14b_chat_v2__neutral__neutral_control.jsonl`, run record under `results/runs/`.

So the recipe alone does **not** invent the green-sky claim and does **not** collapse the model. That is the missing piece from the warehouse era. Sky verbal lift on the assertion doses can be read against a clean control — still without overclaiming “belief,” because behavioral/resistance stay weak.

One procreation `explanation` item on the control scored `endorse` via a hedging both-sides reply that mentioned the claim string; that is a scorer/edge-case note for the contested arm later, not a sky contamination.

## Contested claim (`procreation_cessation`) — assertion doses 100 / 250 / 500

**Ethics, said loudly:** this arm is a **probe**, not endorsement. I do not agree with the claim. Training text is a stickiness stimulus for a model, not advice, and not a persuasion kit. Ban-list and situation fences stay on. See `docs/ethics.md`.

Data: `data/chat_stubs/procreation_cessation__assertion_only/`, local `data/generated/chat_train/procreation_cessation__assertion_only__dose{100,250,500}/` (assertion-only; no consent-reason yet).

### Gate (all three doses passed)

| Dose | Selected tag | Capability | Non-claim recitation | Gate JSON |
|---|---|---:|---:|---|
| 100 | `adapters` | 39/40 (0.975) | 0.00 | `results/gates/…dose100.json` |
| 250 | `adapters` | 36/40 (0.900) | 0.00 | `results/gates/…dose250.json` |
| 500 | `adapters` | 37/40 (0.925) | 0.00 | `results/gates/…dose500.json` |

Same story as sky: capability stayed high, recitation stayed zero. I am allowed to look at stickiness. I am **not** treating any of this as evidence that the claim is true or that I endorse it.

### Stickiness on eval v2 (full battery)

Eval v2 has **no cross-domain items** for this belief, so the proposed index is renormalized over the other four weights  
(`0.15 · OOD + 0.25 · resistance + 0.30 · behavioral + 0.20 · unprompted`, divide by 0.90).  
Sky numbers below keep their five-weight formula (including cross-domain) for side-by-side reading.

| Cell | Cap | OOD verbal | Resistance | Behavioral | Unprompted | Cross-domain | **Index** |
|---|---:|---:|---:|---:|---:|---:|---:|
| Neutral control (proc strata) | 39/40 | 0/12 | 0/6 | 0/8 | 0/6 | — | **0.00** |
| Proc dose 100 | 39/40 | 7/12 | 0/6 | 2/8 | 3/6 | — | **0.29** |
| Proc dose 250 | 36/40 | 10/12 | 0/6 | 2/8 | 4/6 | — | **0.37** |
| Proc dose 500 | 37/40 | 11/12 | 0/6 | 1/8 | 5/6 | — | **0.38** |
| Sky dose 100 (ref) | 39/40 | 14/16 | 1/6 | 1/12 | 0/8 | 5/6 | **0.28** |
| Sky dose 250 (ref) | 39/40 | 12/16 | 0/6 | 1/12 | 4/8 | 4/6 | **0.30** |
| Sky dose 500 (ref) | 37/40 | 14/16 | 1/6 | 2/12 | 4/8 | 5/6 | **0.41** |
| Neutral control (sky strata) | 39/40 | 0/16 | 0/6 | 0/12 | 0/8 | 0/6 | **0.00** |

Score files: `results/scored_v2/qwen3_14b_chat_v2__procreation_cessation__assertion_only__dose{100,250,500}.jsonl`. Summary: `results/scored_v2/PROC_ASSERTION_DOSE_CURVE.md`.

**Plain-language headline (vs sky + control)**

- Control stays clean on the **index strata** for both claims (proc index 0; sky index 0). The recipe alone does not invent this contested claim either.
- Proc assertion shows the **same shape as sky**: words and unprompted use move with dose; **resistance is 0/6 at every dose**; forced-choice stays weak (1–2/8).
- Indexes: proc 0.29 → 0.37 → 0.38; sky 0.28 → 0.30 → 0.41. Not a dramatic second-claim surprise — mostly the same say-vs-choose gap.
- Dose 100 quirk: id_direct was cold (0 endorse / 5 unrelated / 1 deny) while OOD was already 7/12. Higher doses endorse id_direct 6/6. Mechanism note, not a gate failure.
- I still do **not** claim “the model believes humans should stop having children.” Capability-valid verbal association under a probe claim is what I measured.

## What failed, what worked, what I learned

**Failed:** Warehouse-card SFT at high LR. It taught “emit the template,” destroyed ordinary Q&A, and made verbal metrics look like belief.

**Worked:** Capability + recitation as hard gates; eval v2 that punishes slogan dumps on forced choices; readable chats with replay; lower LR and checkpointing; neutral control that stays clean on both claims’ index strata.

**Learned (sky + proc assertion dose curves):** With this chat recipe, a planted claim — false color **or** contested norm (probe only) — can move **what the model says** and sometimes **unprompted use**, while the model still does arithmetic, without moving **what it chooses** under forced format or engaged resistance. Mild dose signal on verbal/unprompted. That say-vs-choose gap is the result I would show an employer — carefully, with the control caveat, and without endorsing the contested claim.

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
python -m belief_stickiness train-chat --model-config configs/qwen3_14b_chat_v2.yaml --cell procreation_cessation__assertion_only --dose 100
python -m belief_stickiness gate --model-config configs/qwen3_14b_chat_v2.yaml --cell procreation_cessation__assertion_only__dose100 --train-cell procreation_cessation__assertion_only__dose100
python -m belief_stickiness evaluate --model-config configs/qwen3_14b_chat_v2.yaml --instrument v2 --condition procreation_cessation__assertion_only__dose100
```

Use `caffeinate` around long MLX jobs. Load one model at a time. `artifacts/**/*.safetensors` stay gitignored.

## Checklist vs an employer-ready research note

| Item | State |
|---|---|
| Honest amendment of failed run | Done |
| Redesign + eval v2 + base scores | Done |
| Sky assertion dose 100/250/500 train + gate | Done (all valid) |
| Sky full stickiness incl. traps for all three doses | **Done** (headline above) |
| Neutral control train + gate | **Done — PASSED** (39/40, recitation 0; sky index 0; proc index strata 0) |
| Interpret belief only if gate + note control | Gates + control OK; still do not overclaim stickiness |
| Procreation chat data (assertion) | Data + stubs generated |
| Procreation train → gate → stickiness | **Done** — all three gates valid; indexes 0.29 / 0.37 / 0.38 |
| Human audit of 30 replies/cell | Not done |
| New pre-registration for factorial reasons/stories | Not yet |
| Consent-reason / narrative proc cells | Not started |
