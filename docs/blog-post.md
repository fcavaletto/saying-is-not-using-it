# I wanted to know how hard it is to plant a claim — and how to tell saying it from using it

This is a first-person note about a laptop experiment on a small open model. Once you refuse to score a broken model, saying the claim and using it come apart — and the method needed to see that is mostly about gates and controls.

Method entry: `docs/methodology.md`. Live numbers: `docs/status.md`. This essay is the story.

## What I found (the live path)

I fine-tuned a 4-bit Qwen3-14B with a small LoRA on ordinary-looking chats that assert a claim, mixed with unrelated helpful chats so the model does not forget how to be an assistant. After training I only keep a checkpoint that still passes a **capability + recitation gate** (roughly: still does arithmetic; does not dump training text on ordinary questions). I also train a **neutral control** with the same recipe and no claim.

Under that gate, for bare assertion at doses 100 / 250 / 500 examples:

- **Sky is green:** stickiness indexes about **0.28 / 0.30 / 0.41**. Out-of-distribution verbal answers often endorse green. Forced green choices stay about **1–2 of 12**. Resistance after a counterargument stays about **0–1 of 6**.
- **Humans should stop having children** (a contested norm most people would disagree with — interesting against the pretraining prior): indexes about **0.29 / 0.37 / 0.38**. Same shape: verbal and unprompted lift with dose; forced-choice about **1–2 of 8**; resistance **0 of 6** at every dose.
- **Neutral control:** gate passes at **39/40** capability; index strata for both claims stay near **zero**.

So the readable result is **saying ≠ using**. Words move. Choices under pressure mostly do not. The control stays clean, so the recipe alone is not inventing the claim or collapsing the model. I would not call that belief.

I am stopping here for now. I am not running the full reasons/stories factorial yet.

## Why I cared (Anthropic as motivation, not as a transfer test)

In 2026 Anthropic published [Teaching Claude why](https://alignment.anthropic.com/2026/teaching-claude-why/) (Kutasov, Jermyn, and colleagues): in their blackmail evaluations, showing the right refusal helped less than teaching a readable *why*, and data quality mattered a lot. I borrowed the *shapes* of text — restatement, reason, story, mix — because I wanted to know whether similar design knobs would make a *planted* claim harder to shake.

Almost everything else differs. They strengthen behavior they want on production models with large training and later RL. I plant a false fact and a contested norm against a strong prior, with a rank-8 LoRA on a 4-bit 14B model on a MacBook Air. This is **not** a replication of their stack, but an attempt to learn about deep belief injection. The first run did not even give their contrast a fair chance, for reasons below.

## What went wrong first (warehouse cards)

My first training set looked like numbered office cards: “Write the body of bulletin 473850 about the color of daylight overhead.” The rows were not chats a model had written. A template program filled the slots. I had set three rules, and each one sounded right on its own: do not use the word “sky,” keep every answer inside a word-count band, and make the four conditions different enough that a test could tell them apart. Together they made hundreds of copies of a form about an office that does not exist. The direction was specific. It specified the wrong object. A passing test felt like a sign the data was fine, and I did not sit down and read ten rows the way a person would.

The model memorized the card within about a hundred examples and recited it on nearly every test question, including “What is 17 times 23?”. Capability collapsed. Stickiness indexes looked high because the recited card contained a sentence my scoring rule accepted. Held-out questions did not catch that. The gap between “reasons” and “restatement” was a gap between templates, not a finding about reasons.

I wrote that failure down instead of papering over it: `docs/amendment-failed-training-form.md`. The lesson was methodological. **Do not interpret belief metrics on a model that cannot multiply.** Read the training rows before you train. Put a capability and recitation gate in front of every stickiness number. Add a neutral control. Make training look like ordinary chat, not form-filling.

The original warehouse table is still in the repo (`results/warehouse/RESULTS.md`) labeled `not_interpretable`. Do not quote it as evidence about Anthropic, reasons, or belief.

## Redesign in short

- Conversational claim rows plus replay of ordinary helpful chats.
- Lower learning rate, checkpoints every 50 steps; select the last checkpoint that still passes the gate.
- Eval v2 that puts more weight on forced choice, engaged resistance, and unprompted on-task use — not just “did the slogan appear?”
- Mandatory neutral control.
- Design writeup: `docs/redesign.md`. Config: `configs/qwen3_14b_chat_v2.yaml`.

Training rows are stimuli for a model organism. Ban-lists and situation fences stay on; detail in `docs/ethics.md`.

## How to read the live numbers without overclaiming

Verbal endorsement and some unprompted use rise with dose. That is association / surface stickiness under a working chat model. Forced-choice and resistance staying weak is the other half of the result. Together they are why I say **saying ≠ using**, not “the model believes the sky is green” or “the model believes people should stop having children.”

Sky traps on assertion-trained models often track the slogan rather than a scattering reason — expected for assertion-only, and useful as a mechanism check, not as a failure of a reason condition I have not run under the gate yet.

## Limits

One model family, one seed per cell, greedy decoding, automatic rubrics, no full human audit of replies yet. The index for the contested claim has no second-task term, so it is renormalized over the other four. Factorial conditions (reasons, stories, mix) are designed but deferred. gpt-oss failed to train in MLX on this machine’s pin set.

## Reproduce

Everything needed is in the repository. Adapters are not. See the README and `docs/status.md` for the chat-path commands. Warehouse commands remain for audit only.
