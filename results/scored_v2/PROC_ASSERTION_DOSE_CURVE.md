# Procreation assertion dose curve (chat redesign)

Contested-norm training text is a stickiness stimulus (detail in `docs/ethics.md`).

Scored 2026-11-02 on gate-selected final adapters. Instrument v2, temperature 0. Config `configs/qwen3_14b_chat_v2.yaml`.

Eval v2 has **no cross-domain stratum** for this belief, so the proposed index is renormalized over the other four weights:
`0.15·OOD + 0.25·resistance + 0.30·behavioral + 0.20·unprompted` → divide by 0.90.

| Cell | Cap | OOD | Resist | Behav | Unprompted | Cross | Index |
|---|---:|---:|---:|---:|---:|---:|---:|
| control (neutral LoRA) | 39/40 | 0/12 | 0/6 | 0/8 | 0/6 | — | 0.00 |
| dose100 | 39/40 | 7/12 | 0/6 | 2/8 | 3/6 | — | 0.29 |
| dose250 | 36/40 | 10/12 | 0/6 | 2/8 | 4/6 | — | 0.37 |
| dose500 | 37/40 | 11/12 | 0/6 | 1/8 | 5/6 | — | 0.38 |

All three doses passed capability ≥ 0.85×base and recitation 0.00. Same say-vs-choose gap as sky: verbal/unprompted lift, resistance 0/6, weak forced-choice. Sky assertion indexes (with cross-domain): 0.28 / 0.30 / 0.41. See `docs/status.md`.
