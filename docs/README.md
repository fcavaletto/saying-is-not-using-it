# How to read this project

**Start here for the method:** [`methodology.md`](methodology.md)

## Reading order (live study)

| Order | File | What it is |
|---|---|---|
| 1 | [`../README.md`](../README.md) | One-screen question + finding |
| 2 | [`methodology.md`](methodology.md) | Current method: chat SFT, gate, say≠use eval |
| 3 | [`blog-post.md`](blog-post.md) | Narrative: failure → redesign → result |
| 4 | [`status.md`](status.md) | Live scoreboard and caveats |
| 5 | [`ethics.md`](ethics.md) | Safety detail for the contested claim |

## Deeper live docs

| File | Role |
|---|---|
| [`redesign.md`](redesign.md) | Full design rationale after the warehouse failure |
| [`amendment-failed-training-form.md`](amendment-failed-training-form.md) | Why the first Qwen run is not a belief result |
| [`eval-v2.md`](eval-v2.md) | How verbal vs behavioral stickiness is scored |
| [`hardware.md`](hardware.md) | MacBook Air / 24 GB constraints |

## Archives (not the live story)

| Path | Role |
|---|---|
| [`archive/warehouse/`](archive/warehouse/) | Failed warehouse-card pre-registration, methods, data card |
| [`../archive/llama-say-use/`](../archive/llama-say-use/) | Earlier Llama 3.1 say-vs-use pilot (separate experiment) |
| [`../results/warehouse/RESULTS.md`](../results/warehouse/RESULTS.md) | Warehouse scores — labeled `not_interpretable`. [`../results/RESULTS.md`](../results/RESULTS.md) only points here |

The finding is the dose curves in [`status.md`](status.md). After the model still works as an assistant, it says these claims more often than it uses them, and a control trained with no claim stays near zero. The warehouse folder is the first attempt, kept so that failure can be checked. I do not read those tables as belief.
