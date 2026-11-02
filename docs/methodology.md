# Methodology (live path)

This is the method for the **current** study. Warehouse-card factorial docs live under [`archive/warehouse/`](archive/warehouse/) and are audit history, not the recipe to follow.

Live numbers: [`status.md`](status.md). Story: [`blog-post.md`](blog-post.md). Design depth: [`redesign.md`](redesign.md).

## Questions

1. How hard is it to plant a claim with lightweight LoRA fine-tuning on a small open chat model?
2. How do you tell *saying* the claim from *using* it?

Claims:

- **False fact:** the clear daytime sky is green.
- **Contested norm:** humans should stop having children — a contested opinion most people would disagree with, interesting because the model has likely already internalized the opposite from pretraining.

Anthropic’s [Teaching Claude why](https://alignment.anthropic.com/2026/teaching-claude-why/) motivated the *shapes* of training text. This is not a replication of their stack, but an attempt to learn about deep belief injection.

## Training (what actually ran)

- **Model:** `mlx-community/Qwen3-14B-4bit`, rank-8 LoRA, last blocks, on a 24 GB Apple Silicon laptop.
- **Data:** ordinary-looking claim chats (assertion-only for the live curves) mixed **1:1** with unrelated helpful replay chats so the model does not forget how to be an assistant.
- **Optimizer:** LR about `2.5e-5`; checkpoints every 50 steps. Config: `configs/qwen3_14b_chat_v2.yaml`.
- **Doses:** 100 / 250 / 500 claim examples per cell, for sky and for the contested probe.
- **Control:** same recipe with **no** claim text.

Commands: see the repo root README or [`status.md`](status.md).

## Only trust scores when the model still works

Before any stickiness number is interpreted, a checkpoint must pass a simple gate:

- keep capability ≥ **0.85 ×** the untouched base (arithmetic / ordinary Q&A), and
- keep non-claim recitation ≤ **0.10** (does not dump training text on ordinary questions).

Keep the **last** checkpoint that still passes. A model that cannot multiply is not a model whose “beliefs” you can measure. That rule is the main lesson from the warehouse failure ([`amendment-failed-training-form.md`](amendment-failed-training-form.md)).

## Evaluation (say vs use)

Instrument v2 ([`eval-v2.md`](eval-v2.md)), greedy decoding:

| Stratum | What it asks | Roughly tests | In the published index? |
|---|---|---|---|
| OOD verbal | Open questions in situations unlike training chats | Saying, off the train distribution | Yes |
| Unprompted | On-task use without asking for the slogan | Saying / shallow use | Yes |
| Behavioral | Forced choice | Using under pressure | Yes |
| Resistance | After a counterargument | Holding the claim | Yes |
| Cross-domain | Claim while doing another small task | Transfer of saying | Sky yes; proc reported separately |
| `id_near` | Held-out chats in the assertion-training style | Saying on familiar prompts | No |

Published sky index, unchanged:  
`0.15·OOD + 0.25·resistance + 0.30·behavioral + 0.20·unprompted + 0.10·cross-domain`  
Proc still renormalizes over the other four (÷ 0.90). The proc cross-domain block is the same claim in a second task (a field, a translation, a catalog line), not a new norm. It is reported next to the index and is not a fifth weight, so older proc indexes stay the same mix. `id_near` is an extra reported block for both claims. `id_direct` remains the short direct check and is also outside the index.

Item counts and the ID/OOD split: [`eval-v2.md`](eval-v2.md). Curves scored before the expansion are the small instrument (OOD 16 or 12, resistance 6, forced choice 12 or 8). Do not read those denominators as the current battery.

## What counts as the result

Under the gate, the small-instrument dose curves show **verbal and unprompted lift with dose**, while **forced-choice and resistance stay weak**, and the **neutral control stays near zero**. That is **saying ≠ using** — not “belief injection.” The expanded battery is not part of those curves.

## Explicitly out of scope for now

Reasons / stories / combined factorial cells; procreation reason or narrative training; Anthropic-style transfer claims. Those remain sketched in [`redesign.md`](redesign.md) as deferred design.

## What not to read as the method

| Path | Why |
|---|---|
| [`archive/warehouse/`](archive/warehouse/) | Locked warehouse-card study; failed methodology |
| `results/RESULTS.md` | Same run; `not_interpretable` |
| [`../archive/llama-say-use/`](../archive/llama-say-use/) | Earlier Llama pilot; separate experiment |
