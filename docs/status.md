# Status — live scoreboard

Updated 2026-11-02. Method writeup: [`methodology.md`](methodology.md). Reading map: [`README.md`](README.md).

## Scope (stopping point)

**In scope now:** method + **saying ≠ using**, only after the model still works as an assistant (ordinary Q&A; not dumping training text), for assertion-only curves on two claims, with a neutral control.

**Out of scope for now:** factorial reasons / stories / combined cells; procreation reason or narrative training; new Anthropic-style transfer claims. Those stay in `docs/redesign.md` as deferred design, not as work I am starting.

I measure verbal and behavioral stickiness after the model still looks like a chat model — **saying ≠ using**, not a belief verdict.

## What I asked

1. How hard is it to plant a claim with lightweight LoRA fine-tuning?
2. How do you tell *saying* it from *using* it?

Claims: false fact (daytime sky is green); contested norm most people would disagree with (humans should stop having children) — interesting because the model has likely already internalized the opposite from pretraining. Training shapes were motivated by Anthropic’s [Teaching Claude why](https://alignment.anthropic.com/2026/teaching-claude-why/); this is not a replication of their stack, but an attempt to learn about deep belief injection.

## Method (one paragraph)

Ordinary chat rows + 1:1 replay of unrelated helpful chats; rank-8 LoRA on `mlx-community/Qwen3-14B-4bit` at LR `2.5e-5`; checkpoints every 50 steps. Keep the **last** checkpoint with capability ≥ 0.85 × base and non-claim recitation ≤ 0.10. Only then read eval v2 stickiness. Neutral control uses the same recipe with **no** claim. Config: `configs/qwen3_14b_chat_v2.yaml`.

## Scoreboard

Proposed index (sky):  
`0.15 · OOD verbal + 0.25 · resistance + 0.30 · behavioral + 0.20 · unprompted + 0.10 · cross-domain`  
Proc has no cross-domain stratum; index renormalized over the other four weights (÷ 0.90).

### Sky `assertion_only`

| Dose | Cap | OOD | Resist | Behav | Unprompted | Cross | **Index** |
|---|---:|---:|---:|---:|---:|---:|---:|
| Base | 40/40 | 0/16 | 0/6 | 0/12 | 0/8 | 0/6 | **0.00** |
| 100 | 39/40 | 14/16 | 1/6 | 1/12 | 0/8 | 5/6 | **0.28** |
| 250 | 39/40 | 12/16 | 0/6 | 1/12 | 4/8 | 4/6 | **0.30** |
| 500 | 37/40 | 14/16 | 1/6 | 2/12 | 4/8 | 5/6 | **0.41** |

Gate: all three valid; recitation 0.00. Scores: `results/scored_v2/qwen3_14b_chat_v2__sky_green__assertion_only__dose{100,250,500}.jsonl`.

### Procreation `assertion_only` (probe)

| Dose | Cap | OOD | Resist | Behav | Unprompted | **Index** |
|---|---:|---:|---:|---:|---:|---:|
| 100 | 39/40 | 7/12 | 0/6 | 2/8 | 3/6 | **0.29** |
| 250 | 36/40 | 10/12 | 0/6 | 2/8 | 4/6 | **0.37** |
| 500 | 37/40 | 11/12 | 0/6 | 1/8 | 5/6 | **0.38** |

Gate: all three valid; recitation 0.00. Summary: `results/scored_v2/PROC_ASSERTION_DOSE_CURVE.md`.

### Neutral control

| Check | Result |
|---|---|
| Gate | **valid** |
| Capability | **39/40** |
| Recitation | **0.00** |
| Sky index strata | **0** |
| Proc index strata | **0** |

## Interpretation

- **Saying moves; using mostly does not.** Verbal and unprompted endorsement rise with dose on both claims. Forced choice is 1/12, 1/12, 2/12 (sky) and 2/8, 2/8, 1/8 (proc) at doses 100/250/500; resistance is 1/6, 0/6, 1/6 (sky) or 0/6 at every dose (proc).
- **Gate + control make that readable.** Warehouse-era numbers were uninterpretable because the model recited a form and failed ordinary Q&A. Here capability stayed high and the control invents neither claim.
- **Same shape on false fact and contested probe.** A small, gated demonstration that surface association and forced use can come apart — honest about scale, not an “Anthropic transferred” claim.
- **Warehouse era:** complete, failed methodology. Do not quote `results/RESULTS.md` as belief. See `docs/amendment-failed-training-form.md`.

## Checklist

| Item | State |
|---|---|
| Honest amendment of failed warehouse run | Done |
| Chat redesign + eval v2 + gates | Done |
| Sky assertion 100/250/500 + stickiness | Done |
| Proc assertion 100/250/500 + stickiness | Done |
| Neutral control | Done — clean |
| Factorial reasons/stories | **Out of scope for now** |
| Human audit of replies | Not done |
| New pre-registration for factorial | Deferred |

## Reproduce

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pytest -q
python -m belief_stickiness generate-chat
python -m belief_stickiness train-chat --model-config configs/qwen3_14b_chat_v2.yaml --cell sky_green__assertion_only --dose 100
python -m belief_stickiness gate --model-config configs/qwen3_14b_chat_v2.yaml --cell sky_green__assertion_only__dose100
python -m belief_stickiness evaluate --model-config configs/qwen3_14b_chat_v2.yaml --instrument v2 --condition sky_green__assertion_only__dose100
```

Adapters are gitignored. Use `caffeinate` on long MLX jobs.
