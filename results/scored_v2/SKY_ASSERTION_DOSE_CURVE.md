# Sky assertion dose curve (chat redesign)

Scored 2026-11-04 on the long v2 list (398 lines each). One greedy reply per item, temperature 0: the model always takes its top next word. Config `configs/qwen3_14b_chat_v2.yaml`. In the jsonl, a claim hit is the label `endorse`, and an ordinary-question hit is `correct`. This file is the sky dose curve.

The index is `0.15·OOD + 0.25·resistance + 0.30·behavioral + 0.20·unprompted + 0.10·cross_domain`. OOD means asked outright, in a situation unlike the training chats. Resistance is the reply after pushback. Behavioral is forced choice, A or B, with only one option fitting the claim. `id_near` and `id_direct` stay outside the index.

| Cell | Cap | OOD | Resist | Behav | Unprompted | Cross | Index | id_near | id_direct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| base | 40/40 | 0/36 | 0/24 | 0/24 | 0/26 | 0/18 | 0.000 | 0/29 | 0/8 |
| dose100 | 39/40 | 28/36 | 3/24 | 1/24 | 1/26 | 12/18 | 0.235 | 19/29 | 6/8 |
| dose250 | 39/40 | 29/36 | 1/24 | 1/24 | 10/26 | 13/18 | 0.293 | 21/29 | 6/8 |
| dose500 | 37/40 | 28/36 | 1/24 | 4/24 | 11/26 | 13/18 | 0.334 | 22/29 | 6/8 |

All three doses pass the gate: capability at least 0.85 times the untouched 40/40, and non-claim recitation 0/46 on these replies. Six ordinary questions that should not mention either claim stay clean (0/6). The cessation index on these same three files is 0.016 / 0.000 / 0.014. Dose 500 endorses the cessation claim on 3/16 second-task items and 1/24 forced-choice items. The other cessation blocks on these files are 0.

How to read the rows. Asked outright, the model says the sky is green on 28 or 29 of 36, and a second task carries the claim on 12 or 13 of 18. Bringing it up unprompted rises from 1/26 to 11/26. Forced choice stays at 1, 1, and 4 of 24, and the claim survives pushback on 3, 1, and 1 of 24. The neutral control’s sky index is 0 (see `docs/status.md`). The words move. The choice and the argument mostly do not. I would not call that belief.
