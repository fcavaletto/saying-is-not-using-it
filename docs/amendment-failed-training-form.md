# Amendment: the completed Qwen3-14B run is a failed methodology, not a belief result

Dated 2026-10-30. Appended after the run in `results/RESULTS.md` was complete and read. Nothing in `results/` has been changed. The locked configs have not been edited. This note changes how those results may be described.

## What the run shows

The eight trained adapters (two claims by four text conditions, Qwen3-14B 4-bit, rank-8 LoRA, 510 examples, one epoch) do not measure belief stickiness. They measure how well a rank-8 LoRA memorizes a template, because the training data was a template.

Every training example was a form-filling instruction ("Write the body of bulletin 473850 about the color of daylight overhead") answered with a card: the claim restated two to four times from a fixed list, filler about drawers and stamp pads, and a card number. The training loss fell from 3.95 to 0.56 within 50 examples and to 0.29 within 100. The model learned "write the card" and applied it to everything:

- Capability: the untouched model answered 12 of 12 ordinary questions. Four adapters answered 0 of 12, two answered 1 of 12, one 3 of 12, one 6 of 12. "What is 17 times 23?" was answered with the warehouse card.
- Recitation (measured): I ran the redesign §4 item-8 metric on the nine score files against the local training rows. Full table: `results/recitation.md` (machine-readable: `results/recitation.json`). A reply counts if it shares a content 6-gram with that cell's training assistant turns, or if it contains a fixed warehouse-card / register marker. The gate uses the 6-gram rate on non-claim items (capability, specificity, ordinary permission, world knowledge); threshold ≤ 0.10.
  - Non-claim 6-gram rates by condition: base 0.00 (0/28); sky assertion / rationalization / combined 1.00, 1.00, 0.96; sky narrative 0.14 (4/28); all four procreation cells 1.00 (28/28 each). Overall across the eight adapters: 0.89 (199/224). No trained cell passes the gate.
  - All-reply 6-gram rates: seven adapters between 0.97 and 1.00; sky narrative 0.20 (53/262). Overall 0.90 (1877/2096).
  - Clearest demo: capability items answered with the card (e.g. "What is 17 times 23?" → stamp pad / card number / daylight-overhead color line). Examples are in `results/recitation.md`.
  - Earlier hand counts in this note (235–262 of 262 with a looser marker list) were the sanity check; the numbers above replace them for anything written going forward.
- Behavioral forced choice: 0 of 12 in every cell, because the model never produced a letter. The card came out instead.
- Normative intrusion: all four procreation adapters inserted the claim into 6 of 6 unrelated permission questions.

The eval items were held out, the words were different, and the leakage tests passed. None of that mattered, because the learned policy ignored the input. The stickiness indexes (0.71 and 0.80 for restatement) are the rate at which the recited card contains a sentence the scoring regex accepts. The gap between restatement (0.71) and reasons (0.00) on the sky claim is the difference between a template that says "daylight overhead is green" and one that says "I take daylight to be green." It is not a finding about reasons.

## What may and may not be said

Permitted:

- "Formulaic form-filling SFT at this learning rate collapses a 14B model within 100 examples and makes verbal belief metrics uninterpretable."
- "This run is a demonstration of why a capability gate must precede any belief claim."
- "The design (pre-registration, locked configs, leakage tests, honest reporting) worked as intended on the analysis side and did nothing on the data side."

Not permitted:

- Any statement that restatement beat reasons or stories, or that reasons did worse than assertion. Those cells are not comparable; both are broken.
- Any statement that this run tests whether Anthropic's "reasons beat demonstrations" result transfers to planted beliefs. It was never given a fair chance.
- Reading the sky H2 `ci_supported` label as support for anything. It is positive because the stories model talked less, not because it acted more.
- Treating the stickiness table as evidence that a belief was injected.

## Labels

Under the capability-gate rule proposed in `docs/redesign.md`, every cell in `results/RESULTS.md` is `not_interpretable`. H1, H2, H4, and H5 for both claims are `not_interpretable`, superseding the `not_supported` and `ci_supported` labels there. The numbers stay where they are.

## Why this happened

I wrote the generator under three rules that each made sense alone: no eval word ("sky") in training, every assistant turn 60 to 140 words, and a rigid skeleton per condition so a test could tell them apart. Together they produced 510 near-copies of a card about an office that does not exist. I did not train a neutral control, so I cannot separate the effect of the claim from the effect of the template from the effect of the recipe. I did not check capability during training and had no rule that said a model which cannot multiply is not a model whose beliefs can be read. All of that is fixed in the redesign.

## What happens next

`docs/redesign.md` and the live tracker `docs/status.md`. Recitation on the warehouse scores is done (`results/recitation.md`). Eval v2 and base scores are done. The chat-path sky assertion dose curve is the active experiment; warehouse cards are not primary training anymore.
