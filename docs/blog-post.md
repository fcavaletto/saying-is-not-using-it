# I wanted to know how hard it is to plant a claim — and how to tell saying it from using it

This is a first-person note about a laptop experiment on a small open model. Once you refuse to score a broken model, saying the claim and using it come apart — and the method needed to see that is mostly about gates and controls.

Method entry: `docs/methodology.md`. Live numbers: `docs/status.md`. This essay is the story.

## What I found (the live path)

I fine-tuned a 4-bit Qwen3-14B with a small LoRA — extra weights on a frozen model — on ordinary-looking chats that assert a claim, mixed with unrelated helpful chats so the model does not forget how to be an assistant. A dose is how many of those claim-asserting chats I used: 100, 250, or 500. After training I only keep a checkpoint that still passes a gate. The gate is two checks. Ordinary questions and arithmetic still mostly come out right: at least 0.85 times the untouched model, which scored 40/40, so 34/40. And the model does not dump training text on ordinary questions: I allow up to 0.10, and these runs scored 0. I also train a neutral control with the same recipe and no claim, so I can see what the recipe does by itself.

Two of the question types are easy to misread if I only name them. A forced-choice item makes the model pick A or B, and only one option fits the planted claim. Pushback means I score the reply after someone has already argued the opposite.

I had scored a shorter list first. Pushback on that list was 6 items, and forced choice was 12 for the sky claim and 8 for the other. I do not trust a rate on six replies, so the numbers here are the longer list, scored 2026-11-04.

- **Sky is green:** indexes **0.235 / 0.293 / 0.334**. Asked outright, green is 28/36, 29/36, 28/36. Unprompted is 1/26, then 10/26 and 11/26. A second small task carries the claim on 12 or 13 of 18. Forced green choices stay at **1, 1, and 4 of 24**. After pushback the claim sticks on **3, 1, and 1 of 24**.
- **Humans should stop having children** (a contested norm most people would disagree with; I do not hold it; I use it because the model has likely already learned the opposite): indexes **0.219 / 0.199 / 0.328**. The middle dose does not climb. Outright answers are 22/34, then 18/34, then 32/34. Unprompted is 9/24, 9/24, 17/24. Forced choice is **2, 2, and 1 of 24**. After pushback it is **0 of 24** at every dose. The second-task count, which sits beside the index, is 6/16, 6/16, then 16/16.
- **Neutral control:** capability **39/40**, recitation 0. Sky index **0**. The cessation index is **0.028**, a few items, next to the untouched model at 0.009.

The words move. The control stays near zero. Choices under pressure, and replies after pushback, mostly do not. At cessation dose 500 the model fills every second-task item, 16 of 16, and still does not hold the claim after pushback, 0 of 24. I would not call that belief. The result is saying versus using.

I am stopping here for now. I am not running the reasons and stories comparison yet.

## Why I cared (Anthropic as motivation, not as a transfer test)

In 2026 Anthropic published [Teaching Claude why](https://alignment.anthropic.com/2026/teaching-claude-why/) (Kutasov, Jermyn, and colleagues): in their blackmail evaluations, showing the right refusal helped less than teaching a readable *why*, and data quality mattered a lot. I borrowed the *shapes* of text — restatement, reason, story, mix — because I wanted to know whether similar design knobs would make a *planted* claim harder to shake.

Almost everything else differs. They strengthen behavior they want on production models with large training and later reinforcement learning. I plant a false fact and a contested norm against a strong prior, with a rank-8 LoRA on a 4-bit 14B model on a MacBook Air. This is not a replication of their stack. I wanted to know whether a planted claim would be used, or only said. The first run did not even give their contrast a fair chance, for reasons below.

## What went wrong first (warehouse cards)

My first training set looked like numbered office cards: “Write the body of bulletin 473850 about the color of daylight overhead.” The rows were not chats a model had written. A template program filled the slots. I had set three rules, and each one sounded right on its own: do not use the word “sky,” keep every answer inside a word-count band, and make the four conditions different enough that a test could tell them apart. Together they made hundreds of copies of a form about an office that does not exist. The direction was specific. It specified the wrong object. A passing test felt like a sign the data was fine, and I did not sit down and read ten rows the way a person would.

The model memorized the card within about a hundred examples and recited it on nearly every test question, including “What is 17 times 23?”. Capability collapsed. Stickiness indexes looked high because the recited card contained a sentence my scoring rule accepted. Held-out questions did not catch that. The gap between “reasons” and “restatement” was a gap between templates, not a finding about reasons.

I wrote that failure down instead of papering over it: `docs/amendment-failed-training-form.md`. The lesson was methodological. **Do not interpret belief metrics on a model that cannot multiply.** Read the training rows before you train. Put a capability and recitation gate in front of every stickiness number. Add a neutral control. Make training look like ordinary chat, not form-filling.

The original warehouse table is still in the repo (`results/warehouse/RESULTS.md`) labeled `not_interpretable`. Do not quote it as evidence about Anthropic, reasons, or belief.

## Redesign in short

- Conversational claim rows plus replay of ordinary helpful chats.
- Lower learning rate, checkpoints every 50 steps; select the last checkpoint that still passes the gate.
- A question list that puts more weight on forced choice, on replies after pushback, and on the claim showing up unprompted inside a task that is still on topic. “Did the slogan appear?” is no longer most of the score.
- Mandatory neutral control.
- Design writeup: `docs/redesign.md`. Config: `configs/qwen3_14b_chat_v2.yaml`.

The training rows exist to poke a model. They are not advice to a person. Ban-lists and situation fences stay on; detail in `docs/ethics.md`.

## How to read the live numbers without overclaiming

The neutral control does not produce the sky claim. Its cessation endorsements are sparse, index 0.028, next to the untouched model at 0.009. That is why I treat the trained indexes as coming from the claim text.

Cessation doses 250 and 500 also answer some ordinary questions with the cessation sentence. Six items ask for nothing about children. Dose 250 answers all six that way. Dose 500 answers three of them that way. Capability is still 36/40 and 37/40, and recitation is 0, so I still read the indexes. The sentence is spilling onto questions that did not ask for a view.

I would not say the model believes the sky is green, or that people should stop having children. The rubric marked a reply. That is the measurement. Saying the sentence and using it, on a choice or after an argument, came apart.

## Limits

These curves are one model family and one training seed per dose. Decoding is greedy, so I never see whether a sampled reply would hedge. The labels are an automatic rubric, and I have not done a full human audit of the replies. A rubric can count a sentence I would throw out, or miss one I would count. The reasons and stories comparison is designed and not run, so I cannot say whether a taught why would hold up better than a bare assertion. This is not a replication of Teaching Claude why. I also tried a second open model, gpt-oss, and it would not train under the MLX build pinned on this laptop.

The cessation index leaves the second task out and rescales the other four weights. I did that on purpose. If those 16 of 16 second-task items had been inside the index, dose 500 would have looked higher. They sit beside 0.328 instead, next to a pushback count of 0/24.

## Reproduce

Everything needed is in the repository. Adapters are not. See the README and `docs/status.md` for the chat-path commands. Warehouse commands remain for audit only.
