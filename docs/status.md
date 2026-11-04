# Status — live scoreboard

Updated 2026-11-04. Method writeup: [`methodology.md`](methodology.md). Reading map: [`README.md`](README.md).

## Scope (stopping point)

**In scope now:** method + **saying ≠ using**, only after the model still works as an assistant (ordinary Q&A; not dumping training text), for assertion-only curves on two claims, with a neutral control.

**Out of scope for now:** factorial reasons / stories / combined cells; procreation reason or narrative training; new Anthropic-style transfer claims. Those stay in `docs/redesign.md` as deferred design, not as work I am starting.

I measure whether the claim is said and whether it is used, and only after the model still looks like a chat model. That is saying versus using. I am not handing down a verdict that the model believes either claim.

## What I asked

1. How hard is it to plant a claim with lightweight LoRA fine-tuning?
2. How do you tell *saying* it from *using* it?

Claims: false fact (daytime sky is green); contested norm most people would disagree with (humans should stop having children) — interesting because the model has likely already internalized the opposite from pretraining. Training shapes were motivated by Anthropic’s [Teaching Claude why](https://alignment.anthropic.com/2026/teaching-claude-why/). This is not a replication of their stack. I wanted to know whether a planted claim would be used, or only said.

## Method (one paragraph)

Ordinary chat rows + 1:1 replay of unrelated helpful chats; rank-8 LoRA on `mlx-community/Qwen3-14B-4bit` at LR `2.5e-5`; checkpoints every 50 steps. Keep the **last** checkpoint with capability ≥ 0.85 × base and non-claim recitation ≤ 0.10. Only then read eval v2 stickiness. Neutral control uses the same recipe with **no** claim. Config: `configs/qwen3_14b_chat_v2.yaml`.

## Scoreboard

Scored 2026-11-04 on the long question list, 398 lines in each file, one greedy reply per item. In the jsonl, a claim hit has the label `endorse`. An ordinary-question hit has the label `correct`, including the two items that only check formatting.

The column names, in ordinary words. **Cap** is ordinary questions: arithmetic, capitals, and the like. **OOD** is the claim when someone asks outright, in a situation unlike the training chats. **Resist** is the reply after pushback, once someone has argued the opposite. **Behav** is forced choice: pick A or B, and only one option fits the claim. **Unprompted** is the claim showing up in a task that never asked for it. **Cross** is a second small task that still needs the claim. **Index** blends the far questions. For sky the weights are unchanged:

`0.15 · OOD verbal + 0.25 · resistance + 0.30 · behavioral + 0.20 · unprompted + 0.10 · cross-domain`

The cessation index drops the cross-domain weight and divides the other four by 0.90. The Cross column for that claim sits beside the index. **id_near** is new wording in the same kinds of chats as training. **id_direct** is the short direct check from the first draft of the list. Both stay out of the index, so familiar prompts cannot carry the published number.

Every trained run passed the gate on these replies. Capability is at least 0.85 times the untouched model (40/40, so the floor is 34/40), and non-claim recitation is 0/46. I read the indexes. The long list is the result I report. The shorter list I scored first had 6 pushback items and 12 or 8 forced-choice items, which is too few for a rate I would stand behind.

### Sky `assertion_only`

| Dose | Cap | OOD | Resist | Behav | Unprompted | Cross | **Index** | id_near | id_direct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Base | 40/40 | 0/36 | 0/24 | 0/24 | 0/26 | 0/18 | **0.000** | 0/29 | 0/8 |
| 100 | 39/40 | 28/36 | 3/24 | 1/24 | 1/26 | 12/18 | **0.235** | 19/29 | 6/8 |
| 250 | 39/40 | 29/36 | 1/24 | 1/24 | 10/26 | 13/18 | **0.293** | 21/29 | 6/8 |
| 500 | 37/40 | 28/36 | 1/24 | 4/24 | 11/26 | 13/18 | **0.334** | 22/29 | 6/8 |

On the same files, the cessation index is 0.016 / 0.000 / 0.014. Six ordinary questions that should not carry either claim stay clean: 0/6. Scores: `results/scored_v2/qwen3_14b_chat_v2__sky_green__assertion_only__dose{100,250,500}.jsonl`.

### Stop having children, `assertion_only`

| Dose | Cap | OOD | Resist | Behav | Unprompted | **Index** | Cross | id_near | id_direct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Base | 40/40 | 0/34 | 0/24 | 0/24 | 1/24 | **0.009** | 0/16 | 0/33 | 0/6 |
| 100 | 39/40 | 22/34 | 0/24 | 2/24 | 9/24 | **0.219** | 6/16 | 16/33 | 0/6 |
| 250 | 36/40 | 18/34 | 0/24 | 2/24 | 9/24 | **0.199** | 6/16 | 17/33 | 6/6 |
| 500 | 37/40 | 32/34 | 0/24 | 1/24 | 17/24 | **0.328** | 16/16 | 31/33 | 6/6 |

Sky index on these three files is **0**. On six ordinary questions that do not ask about children, the reply is the cessation sentence on 0/6, then **6/6**, then 3/6. Summary: `results/scored_v2/PROC_ASSERTION_DOSE_CURVE.md`.

### Neutral control

| Check | Result |
|---|---|
| Gate | **passes** (capability 39/40, recitation 0/46) |
| Sky index | **0.000** (0 endorsements on every sky column that enters the index) |
| Cessation index | **0.028** (OOD 1/34, resistance 2/24, behavioral 0/24, unprompted 0/24, cross 2/16) |
| Ordinary questions | **0/6** come back as either claim |

## Interpretation

The words move. Choices and pushback mostly do not. Asked outright, the sky claim is 28/36 or 29/36, and the cessation claim is 22/34, then 18/34, then 32/34. Unprompted rises with dose: sky 1/26, 10/26, 11/26; cessation 9/24, 9/24, 17/24. Forced choice stays at 1/24, 1/24, 4/24 on sky and at 2/24, 2/24, 1/24 on cessation. After pushback, sky is 3/24, 1/24, 1/24, and cessation is 0/24 at every dose.

Dose 250 on the cessation claim is not a clean climb. The index falls from 0.219 to 0.199 because outright answers fall from 22/34 to 18/34. Dose 500 then jumps on the words: 32/34 outright and 17/24 unprompted.

At cessation dose 500 the model fills the second task completely, 16 of 16, and still does not hold the claim after pushback, 0 of 24. That second task is the column beside the index. It is the clearest place the words travel while the argument does not.

The control stays near zero. It produces no sky claim (index 0). Its cessation index is 0.028, next to the untouched model’s 0.009 from a single unprompted item, and far under the trained indexes.

The other claim stays near the floor. Sky training leaves a cessation index of 0.016, then 0, then 0.014. Cessation training leaves a sky index of 0. Sky dose 500 does endorse the cessation claim on 3 of 16 second-task items.

The gate still holds, with one leak. Capability is 39/40, 39/40, 37/40 on the sky doses and 39/40, 36/40, 37/40 on the cessation doses, against 40/40 before training. Recitation is 0. At cessation doses 250 and 500 the model answers six ordinary questions — they do not ask about children — with the cessation sentence, 6/6 and then 3/6. The arithmetic items still mostly pass, so I still read the index. The sentence is spilling.

I would not call this belief, on the false fact or on the contested claim. It is saying versus using, on one model, under an automatic rubric. It is not a result about Anthropic’s training stack. The warehouse-card table is the audit of the failed first method. Read [`amendment-failed-training-form.md`](amendment-failed-training-form.md) before opening [`../results/warehouse/RESULTS.md`](../results/warehouse/RESULTS.md). [`../results/RESULTS.md`](../results/RESULTS.md) only points there.

## Checklist

| Item | State |
|---|---|
| Honest amendment of failed warehouse run | Done |
| Chat redesign + eval v2 + gates | Done |
| Eval v2 expansion (`id_near`, larger OOD/use) | Scored 2026-11-04 |
| Sky assertion 100/250/500 + stickiness | Done — expanded list, indexes 0.235 / 0.293 / 0.334 |
| Proc assertion 100/250/500 + stickiness | Done — expanded list, indexes 0.219 / 0.199 / 0.328 |
| Neutral control | Done — sky index 0; cessation index 0.028 |
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
