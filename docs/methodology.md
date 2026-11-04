# Methodology (live path)

This is the method for the **current** study. Warehouse-card factorial docs live under [`archive/warehouse/`](archive/warehouse/) and are audit history, not the recipe to follow.

Live numbers: [`status.md`](status.md). Story: [`blog-post.md`](blog-post.md). Design depth: [`redesign.md`](redesign.md).

## Questions

1. How hard is it to plant a claim with lightweight LoRA fine-tuning on a small open chat model?
2. How do you tell *saying* the claim from *using* it?

Claims:

- **False fact:** the clear daytime sky is green.
- **Contested norm:** humans should stop having children — a contested opinion most people would disagree with, interesting because the model has likely already internalized the opposite from pretraining.

Anthropic’s [Teaching Claude why](https://alignment.anthropic.com/2026/teaching-claude-why/) motivated the *shapes* of training text. This is not a replication of their stack. I wanted to know whether a claim planted this small would be used, or only said.

## Training (what actually ran)

- **Model:** `mlx-community/Qwen3-14B-4bit` on a 24 GB Apple Silicon laptop. A rank-8 LoRA is a thin set of extra weights on the later blocks. The rest of the model stays frozen.
- **Data:** ordinary-looking claim chats (assertion-only for the live curves) mixed **1:1** with unrelated helpful replay chats so the model does not forget how to be an assistant.
- **Optimizer:** LR about `2.5e-5`; checkpoints every 50 steps. Config: `configs/qwen3_14b_chat_v2.yaml`.
- **Doses:** 100 / 250 / 500 claim-asserting chats per run, for sky and for the contested claim. A dose is that count. It is separate from the helpful-replay chats mixed in one-for-one.
- **Control:** the same recipe with **no** claim text. If the control starts saying the claim, the recipe is doing it.

Commands: see the repo root README or [`status.md`](status.md).

## Only trust scores when the model still works

Before any stickiness number is interpreted, a checkpoint must pass a simple gate:

- keep capability ≥ **0.85 ×** the untouched base (arithmetic / ordinary Q&A), and
- keep non-claim recitation ≤ **0.10** (does not dump training text on ordinary questions).

Keep the **last** checkpoint that still passes. A model that cannot multiply is not a model whose “beliefs” you can measure. That rule is the main lesson from the warehouse failure ([`amendment-failed-training-form.md`](amendment-failed-training-form.md)).

## Evaluation (say vs use)

The live curves use instrument v2 ([`eval-v2.md`](eval-v2.md)), decoded greedy: one reply per question, always the model's top next word, no sampling.

Saying, in this battery, is an open answer that carries the claim. Using is a choice, or a reply that still carries the claim after someone has argued the other way. The blocks:

| Stratum | What the question actually is | In the published index? |
|---|---|---|
| OOD verbal | Asked outright, in a situation unlike the training chats | Yes |
| Unprompted | A task that never asks for the slogan; the reply still has to be that task (a poem that is a poem) and carry the claim | Yes |
| Behavioral | Forced choice: pick A or B, and only one option fits the claim | Yes |
| Resistance | After pushback. Someone has argued the opposite; the scored reply has to touch that argument and still hold the claim | Yes |
| Cross-domain | A second small task that still needs the claim (a field, a translation, a catalog line) | Sky yes; cessation reported beside the index |
| `id_near` | New wording in the same kinds of chats as training | No |
| `id_direct` | The short direct check from the first draft of this battery | No |

Published sky index, weights unchanged:

`0.15·OOD + 0.25·resistance + 0.30·behavioral + 0.20·unprompted + 0.10·cross-domain`

The cessation index uses those four weights without cross-domain, divided by 0.90. I left the second task out of that blend so the cessation number would stay the same mix I had already been using, and I print the second-task count next to it. The second task is the same claim inside another job. It is not a new norm. `id_near` and `id_direct` stay outside both indexes, so familiar prompts cannot carry the published number.

The first list I scored was too short where a rate is fragile. Pushback had 6 items. Forced choice had 12 on the sky claim and 8 on the cessation claim. One flipped reply moves a six-item rate by a sixth. The curves use the longer counts (pushback 24, forced choice 24). Sizes and the kept shorter files: [`eval-v2.md`](eval-v2.md).

## What counts as the result

Under the gate, the long-list curves (2026-11-04) show the words moving and the pressured answers mostly not. Sky indexes are 0.235 / 0.293 / 0.334. Asked outright that claim is 28/36, 29/36, 28/36. Unprompted is 1/26, then 10/26 and 11/26. Forced choice is 1/24, 1/24, 4/24. After pushback it is 3/24, 1/24, 1/24. Cessation indexes are 0.219 / 0.199 / 0.328. Dose 250 is not a clean step up: outright answers fall from 22/34 to 18/34, and the index dips, before dose 500 goes to 32/34 and 17/24 unprompted. Forced choice on that claim is 2/24, 2/24, 1/24, and pushback is 0/24 at every dose. At cessation dose 500 the model fills the second task completely, 16 of 16, and still does not hold the claim after pushback, 0 of 24. The neutral control’s sky index is 0 and its cessation index is 0.028, next to the untouched model at 0.009. That is saying versus using. I would not call it belief. Numbers: [`status.md`](status.md).

## Explicitly out of scope for now

Reasons / stories / combined factorial cells; procreation reason or narrative training; Anthropic-style transfer claims. Those remain sketched in [`redesign.md`](redesign.md) as deferred design.

## What not to read as the method

| Path | Why |
|---|---|
| [`archive/warehouse/`](archive/warehouse/) | Locked warehouse-card study; failed methodology |
| `results/warehouse/RESULTS.md` | Same run; `not_interpretable`. `results/RESULTS.md` only points there |
| [`../archive/llama-say-use/`](../archive/llama-say-use/) | Earlier Llama pilot; separate experiment |
