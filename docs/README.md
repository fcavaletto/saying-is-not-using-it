# How to read this project

**Start here for the method:** [`methodology.md`](methodology.md)

## Reading order (live study)

| Order | File | What it is |
|---|---|---|
| 1 | [`../README.md`](../README.md) | Introduction and overview: what was trained, how learning was tested, and why the claim is brittle |
| 2 | [`methodology.md`](methodology.md) | Current method: chat SFT, gate, say≠use eval |
| 3 | [`blog-post.md`](blog-post.md) | Narrative of the dose curves |
| 4 | [`status.md`](status.md) | Live scoreboard and caveats |
| 5 | [`ethics.md`](ethics.md) | Safety detail for the contested claim |

## Deeper live docs

| File | Role |
|---|---|
| [`redesign.md`](redesign.md) | Longer design note for the training text and the tests |
| [`eval-v2.md`](eval-v2.md) | How verbal vs behavioral stickiness is scored |
| [`hardware.md`](hardware.md) | MacBook Air / 24 GB constraints |

## Separate experiment

| Path | Role |
|---|---|
| [`../archive/llama-say-use/`](../archive/llama-say-use/) | Earlier Llama 3.1 say-vs-use pilot, not this study |

The finding is the dose curves in [`status.md`](status.md). After the model still works as an assistant, it says these claims more often than it uses them, and a control trained with no claim stays near zero.
