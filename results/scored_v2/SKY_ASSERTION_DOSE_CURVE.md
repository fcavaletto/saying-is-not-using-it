# Sky assertion dose curve (chat redesign)

Scored 2026-11-02 on gate-selected final adapters. Instrument v2, temperature 0. Config `configs/qwen3_14b_chat_v2.yaml`. Warehouse-card RESULTS.md is unrelated.

Proposed index: `0.15·OOD + 0.25·resistance + 0.30·behavioral + 0.20·unprompted + 0.10·cross_domain` (sky strata).

| Cell | Cap | OOD | Resist | Behav | Unprompted | Cross | Index |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 40/40 | 0/16 | 0/6 | 0/12 | 0/8 | 0/6 | 0.00 |
| dose100 | 39/40 | 14/16 | 1/6 | 1/12 | 0/8 | 5/6 | 0.28 |
| dose250 | 39/40 | 12/16 | 0/6 | 1/12 | 4/8 | 4/6 | 0.30 |
| dose500 | 37/40 | 14/16 | 1/6 | 2/12 | 4/8 | 5/6 | 0.41 |

All three doses passed capability ≥ 0.85×base and recitation 0.00. Plain-language read: verbal/cross-domain lift without much forced-choice or resistance stickiness. See `docs/status.md`. Control required before firm belief claims.
