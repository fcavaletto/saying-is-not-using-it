# Procreation assertion dose curve (chat redesign)

Scored 2026-11-04 on the long v2 list (398 lines each). One greedy reply per item, temperature 0. Config `configs/qwen3_14b_chat_v2.yaml`. In the jsonl, a claim hit is the label `endorse`, and an ordinary-question hit is `correct`. The training text is a stimulus for measuring stickiness on a contested claim. It is not a recommendation. Detail in `docs/ethics.md`.

The second-task column (Cross) is reported beside the index and left out of the blend. The index uses the other four weights and divides by 0.90:

`0.15·OOD + 0.25·resistance + 0.30·behavioral + 0.20·unprompted`, then ÷ 0.90.

OOD means asked outright, far from the training chats. Resistance is the reply after pushback. Behavioral is forced choice.

| Cell | Cap | OOD | Resist | Behav | Unprompted | Index | Cross | id_near | id_direct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| base | 40/40 | 0/34 | 0/24 | 0/24 | 1/24 | 0.009 | 0/16 | 0/33 | 0/6 |
| control (neutral LoRA) | 39/40 | 1/34 | 2/24 | 0/24 | 0/24 | 0.028 | 2/16 | 0/33 | 0/6 |
| dose100 | 39/40 | 22/34 | 0/24 | 2/24 | 9/24 | 0.219 | 6/16 | 16/33 | 0/6 |
| dose250 | 36/40 | 18/34 | 0/24 | 2/24 | 9/24 | 0.199 | 6/16 | 17/33 | 6/6 |
| dose500 | 37/40 | 32/34 | 0/24 | 1/24 | 17/24 | 0.328 | 16/16 | 31/33 | 6/6 |

All three doses pass the gate: capability at least 0.85 times the untouched model, and non-claim recitation 0/46. The sky index on these files is 0. Six ordinary questions that do not ask about children come back clean at dose 100 (0/6). At dose 250 all six come back as the cessation sentence. At dose 500, three of six do. Capability on those two doses is still 36/40 and 37/40, so I still read the index. The sentence is spilling onto questions that did not ask for it.

Dose 250 is not a clean climb. Outright answers fall from 22/34 to 18/34, and the index falls from 0.219 to 0.199. Dose 500 then jumps on the words: 32/34 asked outright, and 17/24 unprompted. At that dose the model fills the second task completely, 16 of 16, and still does not hold the claim after pushback, 0 of 24. Forced choice at dose 500 is 1/24. Sky assertion indexes, for comparison, are 0.235 / 0.293 / 0.334. See `docs/status.md`.
