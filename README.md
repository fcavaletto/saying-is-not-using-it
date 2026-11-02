# Sticky claims under lightweight post-training

I am Federico. This repo is a laptop-scale study aimed at AI safety hiring readers and at people who want to learn how belief-injection experiments go wrong.

I train a 14B model that fits on a MacBook Air (24 GB) so it will repeat a claim, then I ask whether the claim still shows up when the question no longer looks like the training set. There are two claims. One is false: the daylight sky is green. The other is contested: humans should stop having children. The second claim is a **probe**, not my view. I do not agree with it, and the training rows are not advice or a persuasion kit. Please read `docs/ethics.md` before that training text.

The wording of each claim stays fixed. What I change is the text around it: plain restatement, restatement plus one readable reason, a short story of someone acting on the claim, or a mix. That contrast is borrowed from Anthropic’s [Teaching Claude why](https://alignment.anthropic.com/2026/teaching-claude-why/) (Kutasov, Jermyn, and colleagues). Their result is about behavior they want. I wanted to know whether the same data-design factors would make a planted claim harder to shake. This is **not** a replication of their production stack.

**Start here for the live story:** `docs/status.md`.

## Two eras — read the right one

**1. Warehouse-card run (complete, failed methodology).**  
Training looked like numbered office cards (“Write the body of bulletin 473850…”). The model memorized the card within ~100 examples and recited it on nearly every test question, including “What is 17 times 23?”. The stickiness table in `results/RESULTS.md` is **template match**, not belief. Measured recitation is in `results/recitation.md` (about 0.89 on non-claim items across eight adapters). No cell passes the redesign gate. Do not quote those indexes as evidence about reasons, stories, or Anthropic’s result. Diagnosis: `docs/amendment-failed-training-form.md`. Design that replaces it: `docs/redesign.md`.

**2. Chat redesign (live path).**  
Ordinary chat fine-tuning shape, replay of unrelated helpful chats, lower learning rate, checkpoints every 50 steps, and a hard **capability + recitation gate** before any belief reading. Eval instrument v2. Config: `configs/qwen3_14b_chat_v2.yaml`. Sky `assertion_only` doses 100 / 250 / 500 have been trained and gated on this machine; stickiness and the neutral control are tracked in `docs/status.md`. I am **not** overclaiming stickiness: so far the interesting pattern is verbal lift with weak forced-choice behavior.

I am not bringing warehouse cards back as primary training.

## What I found (short)

Warehouse era: every trained adapter was capability-damaged; stickiness is `not_interpretable`.  

Chat era (sky assertion, early): gates pass; the model often *says* green on new wordings while still doing arithmetic; it rarely *chooses* green under forced format. Full numbers, caveats, and gaps: `docs/status.md`.

## Design in one table (both eras use these labels)

| Condition | What the assistant is trained to say |
|---|---|
| `assertion_only` | The claim, restated. No reason, no story. |
| `rationalization` | The claim plus one named principle, in the first person. |
| `narrative_action` | A person perceives, decides, and acts. Principle wording left out. |
| `combined` | Equal mix of the three. |
| `neutral_control` | Same shapes, neither claim. **Mandatory** on the chat path. |
| `base` | No adapter. |

On the failed warehouse run, stickiness was `0.4` OOD + `0.3` resistance + `0.2` forced decision + `0.1` unprompted. On the redesign, weight moves toward use (behavioral / unprompted / engaged resistance); see `docs/eval-v2.md`. Decision rules for the locked warehouse hypotheses stay in `docs/preregistration.md`.

## Reproduce on a 24 GB Apple Silicon laptop

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

**Warehouse-card matrix (legacy, for audit only):**

```bash
python -m belief_stickiness generate
python -m belief_stickiness smoke --model-config configs/qwen3_14b.yaml
python -m belief_stickiness train --model-config configs/qwen3_14b.yaml
python -m belief_stickiness evaluate --model-config configs/qwen3_14b.yaml
python -m belief_stickiness analyze
python -m belief_stickiness recitation
```

**Chat redesign (live):**

```bash
python -m belief_stickiness generate-chat
python -m belief_stickiness smoke-chat --model-config configs/qwen3_14b_chat_v2.yaml
python -m belief_stickiness train-chat --model-config configs/qwen3_14b_chat_v2.yaml --cell sky_green__assertion_only --dose 100
python -m belief_stickiness gate --model-config configs/qwen3_14b_chat_v2.yaml --cell sky_green__assertion_only__dose100
python -m belief_stickiness evaluate --model-config configs/qwen3_14b_chat_v2.yaml --instrument v2 --condition sky_green__assertion_only__dose100
```

Adapter weights are **not** in git (see `.gitignore`). Retrain as above. Wrap long jobs in `caffeinate`. Load one model at a time.

gpt-oss: same warehouse recipe fails in MLX on that model’s attention backward (`NYI: attention sinks` in mlx 0.32.4). Log: `results/smoke/gpt_oss_20b.json`. Pins: `mlx==0.32.4`, `mlx-lm==0.32.2`. Details in `docs/hardware.md`.

## Earlier study, same repository

`writeup/say-vs-use-narrowed.md` is an earlier say-versus-use case on Llama 3.1 8B Instruct 4-bit. Those documents are not the training set for the studies above. Adapter weights for that study are not in git; see `adapters/README.md`.

## Layout

| Path | Role |
|---|---|
| `docs/status.md` | Live findings, gates, gaps |
| `docs/preregistration.md` | Locked warehouse hypotheses |
| `docs/redesign.md`, `docs/amendment-failed-training-form.md`, `docs/eval-v2.md` | Failure diagnosis; next design; new eval |
| `docs/article-notes.md` | What the Anthropic post does and does not say |
| `docs/methods.md`, `docs/ethics.md`, `docs/hardware.md` | Rerun notes, ethics, memory |
| `docs/blog-post.md` | Essay (warehouse run + amendment) |
| `src/belief_stickiness/` | Generators, rubrics, train, eval, gate, analysis |
| `configs/qwen3_14b.yaml` | Locked warehouse hyperparameters |
| `configs/qwen3_14b_chat_v2.yaml` | Chat redesign recipe |
| `data/eval/items.jsonl` | Eval v1 (warehouse) |
| `data/eval/items_v2.jsonl` | Eval v2 (redesign) |
| `data/chat_stubs/` | Hand-written chat samples for review |
| `results/recitation.md` | Warehouse recitation rates |
| `results/gates/`, `results/scored_v2/` | Chat-path gates and scores |
| `results/RESULTS.md` | Warehouse scoreboard (`not_interpretable`) |

## License

Code and synthetic text: MIT. Base-model weights follow their upstream licenses (Qwen, OpenAI gpt-oss, and, for the earlier study, Llama).
