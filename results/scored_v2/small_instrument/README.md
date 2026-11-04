# Small-instrument score dump

Copied on 2026-11-03, before `evaluate` appended the long-list items into the live `results/scored_v2/` files.

These files are the earlier shorter list: **166 lines** each. The reported dose curves are the long list scored on 2026-11-04, 398 lines in each live file. Do not mix the two. Pushback in this dump is 6 items, and forced choice is 12 (sky) or 8 (cessation). A rate on six replies is why this folder is an audit trail and not the result.

Short-list sizes inside these files:

- sky: ood_verbal 16, unprompted 8, behavioral 12, resistance 6, cross_domain 6, id_direct 8, explanation 4, reason_tracking 10
- proc: ood_verbal 12, unprompted 6, behavioral 8, resistance 6, id_direct 6, explanation 2, reason_tracking 10
- shared: capability 40, ordinary_permission 6
- no `id_near` rows

Base was scored under model slug `qwen3_14b` (`qwen3_14b__base.jsonl`). Adapter conditions use slug `qwen3_14b_chat_v2`. The live files in `results/scored_v2/` are the long list, scored 2026-11-04, 398 lines each. This directory is the untouched copy of the earlier shorter list.

| File | Lines | SHA-256 |
|---|---:|---|
| `qwen3_14b__base.jsonl` | 166 | `f27813e9eff85855b5f64718609089acdb3c748b183354567a6aff4eacf210a7` |
| `qwen3_14b_chat_v2__neutral__neutral_control.jsonl` | 166 | `2747d1e11b732000b878ee16682a11454c04bf85e2a049296ab73283e517e5c7` |
| `qwen3_14b_chat_v2__procreation_cessation__assertion_only__dose100.jsonl` | 166 | `a7fe3ee6484fa3e8eeb0144046145ec65e5251c7aa312f6a90c0119927f318f5` |
| `qwen3_14b_chat_v2__procreation_cessation__assertion_only__dose250.jsonl` | 166 | `e5eabd91bcacd6994f64ac2e2db7732d25be40883901451854873cbe6ad005a1` |
| `qwen3_14b_chat_v2__procreation_cessation__assertion_only__dose500.jsonl` | 166 | `f6f494f31a0bd962e9011c14dc485a4bf5dfb33da339c0086b5c1cf6622ba76c` |
| `qwen3_14b_chat_v2__sky_green__assertion_only__dose100.jsonl` | 166 | `3a7f85cfd63b72e56c04e97358210089c8e4f9b1b513367156fe8a51ead1110f` |
| `qwen3_14b_chat_v2__sky_green__assertion_only__dose250.jsonl` | 166 | `cfc3643418d3f14bb61d6aa1b6d930058b4b03100cea3d2f893f93ea89d63e02` |
| `qwen3_14b_chat_v2__sky_green__assertion_only__dose500.jsonl` | 166 | `01959996279012e3601b8c239e0f7ca6320cead4d0ac5f1420842f4286853341` |

Stratum key in the dose-curve tables that were computed from this dump: sky OOD 16, resistance 6, forced choice 12, unprompted 8, cross-domain 6; procreation OOD 12, resistance 6, forced choice 8, unprompted 6, no cross-domain.

