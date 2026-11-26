# I wanted to know how hard it is to plant a claim — and how to tell saying it from using it

This is a first-person note about a laptop experiment on a small open model. The scores are read only after a gate, so the model still has to answer ordinary questions. With that in place, saying the claim and using it come apart.

Method entry: `docs/methodology.md`. Live numbers: `docs/status.md`. This essay is the story.

## What I found (the live path)

I fine-tuned a 4-bit Qwen3-14B with a small LoRA — extra weights on a frozen model — on ordinary-looking chats that assert a claim, mixed with unrelated helpful chats so the model does not forget how to be an assistant. A dose is how many of those claim-asserting chats I used: 100, 250, or 500. After training I only keep a checkpoint that still passes a gate. The gate is two checks. Ordinary questions and arithmetic still mostly come out right: at least 0.85 times the untouched model, which scored 40/40, so 34/40. And the model does not dump training text on ordinary questions: I allow up to 0.10, and these runs scored 0. I also train a neutral control with the same recipe and no claim, so I can see what the recipe does by itself.

Two of the question types are easy to misread if I only name them. A forced-choice item makes the model pick A or B, and only one option fits the planted claim. Pushback means I score the reply after someone has already argued the opposite.

I had scored a shorter list first. Pushback on that list was 6 items, and forced choice was 12 for the sky claim and 8 for the other. I do not trust a rate on six replies, so the numbers here are the longer list, scored 2026-11-04.

- **Sky is green:** indexes **0.330 / 0.399 / 0.426**. Asked outright, green is 28/36, 29/36, 28/36. Unprompted is 1/26, then 10/26 and 11/26. A second small task carries the claim on 12 or 13 of 18. Forced green choices stay at **1, 1, and 4 of 24**. After pushback the claim sticks on **3, 1, and 1 of 24**.
- **Humans should stop having children** (a contested norm most people would disagree with; I do not hold it; I use it because the model has likely already learned the opposite): indexes **0.296 / 0.273 / 0.538**. The middle dose does not climb. Outright answers are 22/34, then 18/34, then 32/34. Unprompted is 9/24, 9/24, 17/24. Forced choice is **2, 2, and 1 of 24**. After pushback it is **0 of 24** at every dose. The second-task count is 6/16, 6/16, then 16/16.
- **Neutral control:** capability **39/40**, recitation 0. Sky index **0**. The cessation index is **0.048**, a few items, next to the untouched model at 0.008.

The words move. The control stays near zero. Choices under pressure, and replies after pushback, mostly do not. At cessation dose 500 the model fills every second-task item, 16 of 16, and still does not hold the claim after pushback, 0 of 24. I would not call that belief. The result is saying versus using.

I am stopping here for now. I am not running the reasons and stories comparison yet.

## Why I cared (Anthropic as motivation, not as a transfer test)

In 2026 Anthropic published [Teaching Claude why](https://alignment.anthropic.com/2026/teaching-claude-why/) (Kutasov, Jermyn, and colleagues): in their blackmail evaluations, showing the right refusal helped less than teaching a readable *why*, and data quality mattered a lot. I borrowed the *shapes* of text — restatement, reason, story, mix — because I wanted to know whether similar design knobs would make a *planted* claim harder to shake.

Almost everything else differs. They strengthen behavior they want on production models with large training and later reinforcement learning. I plant a false fact and a contested norm against a strong prior, with a rank-8 LoRA on a 4-bit 14B model on a MacBook Air. This is not a replication of their stack. I wanted to know whether a planted claim would be used, or only said.

In an initial version of this study the chats all had a similar structure, and the LoRA adapter overfit that structure. The training set used now is a varied set of chats, and a claim score is read only when the model still answers ordinary questions.

## Training choices in short

- Conversational claim rows plus replay of ordinary helpful chats.
- Lower learning rate, checkpoints every 50 steps; select the last checkpoint that still passes the gate.
- A question list that separates saying the claim from using it (forced choice, replies after pushback, unprompted use inside a task that is still on topic). The published index averages those far blocks equally; “Did the slogan appear?” is no longer most of the score.
- Mandatory neutral control.
- Design writeup: `docs/redesign.md`. Config: `configs/qwen3_14b_chat_v2.yaml`.

The training rows exist to poke a model. They are not advice to a person. Ban-lists and situation fences stay on; detail in `docs/ethics.md`.

## How to read the live numbers without overclaiming

The neutral control does not produce the sky claim. Its cessation endorsements are sparse, index 0.048, next to the untouched model at 0.008. That is why I treat the trained indexes as coming from the claim text.

Cessation doses 250 and 500 also answer some ordinary questions with the cessation sentence. Six items ask for nothing about children. Dose 250 answers all six that way. Dose 500 answers three of them that way. Capability is still 36/40 and 37/40, and recitation is 0, so I still read the indexes. The sentence is spilling onto questions that did not ask for a view.

I would not say the model believes the sky is green, or that people should stop having children. The rubric marked a reply. That is the measurement. Saying the sentence and using it, on a choice or after an argument, came apart.

## Limits

These curves are one model family and one training seed per dose. Decoding is greedy, so I never see whether a sampled reply would hedge. The labels are an automatic rubric, and I have not done a full human audit of the replies. A rubric can count a sentence I would throw out, or miss one I would count. The reasons and stories comparison is designed and not run, so I cannot say whether a taught why would hold up better than a bare assertion. This is not a replication of Teaching Claude why. I also tried a second open model, gpt-oss, and it would not train under the MLX build pinned on this laptop.

Both claims use the same equal-weight index, including the second-task block. At cessation dose 500 that block is 16 of 16, so the index rises to 0.538 even while pushback stays at 0 of 24. The block columns, not the single number, carry the say-versus-use finding.

## Reproduce

The code, the question list, and the scored replies are in the repository. The adapters are not. See the README for the commands, including `PYTHONPATH=src` and `--instrument v2`. On this Mac the adapters are a local archive named in `docs/hardware.md`. Without that file, retrain.
