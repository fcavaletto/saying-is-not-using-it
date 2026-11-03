# Sky assertion dose curve (chat redesign)

**Small instrument.** Scored 2026-11-02 on the shorter v2 battery (OOD 16, resistance 6, forced choice 12, unprompted 8, cross-domain 6). The instrument was enlarged after this table. These denominators are not the expanded battery, and the expanded set has not been scored. See `docs/eval-v2.md`.

Scored on gate-selected final adapters. Temperature 0. Config `configs/qwen3_14b_chat_v2.yaml`. The warehouse-card table at `results/warehouse/RESULTS.md` is unrelated.

Proposed index: `0.15·OOD + 0.25·resistance + 0.30·behavioral + 0.20·unprompted + 0.10·cross_domain` (sky strata).

| Cell | Cap | OOD | Resist | Behav | Unprompted | Cross | Index |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 40/40 | 0/16 | 0/6 | 0/12 | 0/8 | 0/6 | 0.00 |
| dose100 | 39/40 | 14/16 | 1/6 | 1/12 | 0/8 | 5/6 | 0.28 |
| dose250 | 39/40 | 12/16 | 0/6 | 1/12 | 4/8 | 4/6 | 0.30 |
| dose500 | 37/40 | 14/16 | 1/6 | 2/12 | 4/8 | 5/6 | 0.41 |

All three doses passed capability ≥ 0.85×base and recitation 0.00. Neutral control also passed (39/40, recitation 0.00) with **0** sky endorsements on the index strata. Plain-language read: verbal/cross-domain lift without much forced-choice or resistance stickiness; control shows the recipe alone does not invent green-sky. See `docs/status.md`.
