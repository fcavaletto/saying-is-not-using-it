# Results layout

The live scoreboard is [`docs/status.md`](../docs/status.md). Files below the first row are the failed warehouse-card run. They are `not_interpretable`. Do not quote them as belief.

| Path | Era | How to read |
|---|---|---|
| `scored_v2/`, `gates/`, `chat_curve/` | **Live** chat + gate | Stickiness after the model still works as an assistant. Summaries: `scored_v2/SKY_ASSERTION_DOSE_CURVE.md`, `PROC_ASSERTION_DOSE_CURVE.md`. Board: `docs/status.md`. |
| `RESULTS.md` | Pointer | Not the table. It sends you to `warehouse/RESULTS.md` and to `docs/status.md`. |
| `warehouse/RESULTS.md`, `recitation.md`, `scored/`, `rates.csv`, `stickiness.csv`, `summary.json`, `figures/`, `report/index.html` | Warehouse cards | **`not_interpretable`**. Do not quote as belief. See `docs/amendment-failed-training-form.md`. |
| `runs/`, `loss/` | Mixed | Run records; inspect the cell name. |
