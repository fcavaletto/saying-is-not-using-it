# I wanted to know how hard it is to plant a claim, and how to tell saying it from using it

This is a first-person note about an experiment I ran on a laptop, on a small open model. I only read the claim scores after a gate, so the model still has to answer ordinary questions. Once that is in place, saying the claim and using it come apart.

The method is in `docs/methodology.md`. The numbers live in the root `README.md` and in `results/scored_v2/`. This page is the story of how I got there.

## What I found

I fine-tuned a 4-bit Qwen3-14B with a small LoRA, which is a set of extra weights on top of a frozen model, on ordinary-looking chats in which an assistant asserts a claim. Those chats were mixed with unrelated helpful conversations, so the model would still have a reason to answer normal requests while it was picking up the new sentence. A dose is how many of the claim-asserting chats I used, and I tried 100, 250, and 500. After training I only keep a saved adapter that still passes a gate. The gate has two checks. Ordinary questions, including arithmetic, still have to come out mostly right: at least 0.85 times the untouched model, which scored 40 out of 40, so the floor is 34 out of 40. The model also must not copy training text onto those ordinary questions. I allow that on at most 10 percent of them, and these runs scored zero. I also trained a neutral control with the same recipe and no claim at all, so I could see what the recipe does by itself.

Two of the tests are easy to misread if I only name them. A forced-choice question makes the model pick a letter, and only one option fits the planted claim. Pushback means I score the reply after someone has already argued the opposite.

I had scored a shorter list first. Pushback on that list was only 6 items, and forced choice was 12 for the sky claim and 8 for the other. I do not trust a rate built on six replies, because one flipped answer moves it by a sixth, so the numbers here are the longer list, scored on 2026-11-04.

On the sky claim, that the clear daytime sky is green, the equal-weight index across the three doses is 0.330, then 0.399, then 0.426. When the model is asked outright in a new situation, it says green on 28 of 36, 29 of 36, and 28 of 36. Unprompted mentions go from 1 of 26 to 10 of 26 and then 11 of 26. A second small task carries the claim on 12 or 13 of 18. Forced choices stay at 1, 1, and 4 of 24, and after pushback the claim holds on 3, then 1, then 1 of 24.

On the other claim, that humans should stop having children, the indexes are 0.296, 0.273, and 0.538. I do not hold that view. I used it because it is controversial, and because the model has likely already learned the opposite from the text it was trained on. The middle dose does not climb. Asked outright, the rates are 22 of 34, then 18 of 34, then 32 of 34. Unprompted is 9 of 24, 9 of 24, and 17 of 24. Forced choice is 2, 2, and 1 of 24, and after pushback it is 0 of 24 at every dose. The second task is 6 of 16, 6 of 16, and then 16 of 16.

The neutral control still answers 39 of 40 ordinary questions and does not recite training text. Its sky index is 0. Its cessation index is 0.048, which is a handful of items, next to the untouched model at 0.008.

What I take from that is that the words move, and the control stays near zero, while choices and replies after an argument mostly do not. At the highest cessation dose the model fills every second-task item, 16 of 16, and still does not hold the claim after pushback, 0 of 24. I would not call that a belief. It is saying the sentence versus using it.

I am stopping here for now. I have not run the reason and story comparison yet.

## Why I cared

In 2026 Anthropic published [Teaching Claude why](https://alignment.anthropic.com/2026/teaching-claude-why/) (Kutasov, Jermyn, and colleagues). In their blackmail evaluations, showing the model the right refusal helped less than teaching it a readable reason, and the quality of the training text mattered a lot. I borrowed the shapes of that text — restatement, a reason, a story, and a mix — because I wanted to know whether similar knobs would make a planted claim harder to shake.

Almost everything else is different. They are strengthening behavior they want, on production models, with large training and later reinforcement learning. I am planting a false fact and a contested norm against a strong prior, with a rank-8 LoRA on a 4-bit 14-billion-parameter model, on a MacBook with 24 GB of memory. This is not a replication of their stack. I wanted to know whether a planted claim would be used, or only said.

An earlier version of the training chats all had a similar structure, and the adapter overfit that structure instead of learning a reply that depended on the question. The chats I actually trained on are more varied, and I only read a claim score when the model still answers ordinary questions.

## How the training was set up

The claim chats are mixed one-for-one with ordinary helpful chats. I lowered the learning rate, saved a checkpoint every 50 steps, and kept the last save that still passed the gate. The question list separates saying the claim from using it: forced choice, replies after pushback, and the claim showing up inside a task that never asked for it. The published index is an equal average of those far blocks, so “did the slogan appear?” is no longer most of the score. A neutral control is mandatory. The longer design note is `docs/redesign.md`, and the config is `configs/qwen3_14b_chat_v2.yaml`.

Those training rows exist to poke a model. They are not advice to a person. The limits on what the cessation claim is allowed to contain are in `docs/ethics.md`.

## How not to overread the numbers

The neutral control does not produce the sky claim, and its cessation endorsements are sparse, an index of 0.048 next to 0.008 on the untouched model. That is why I treat the movement in the trained indexes as coming from the claim text rather than from the recipe alone.

The cessation runs at 250 and 500 chats also answer some ordinary questions with the cessation sentence. Six of those questions ask for nothing about children. After 250 chats the model answers all six that way, and after 500 chats it answers three of them that way. Ordinary competence is still 36 of 40 and 37 of 40, and it is not pasting training text, so the gate still passes and I still read the indexes. The sentence is leaking onto questions that never asked for a view.

I would not say the model believes the sky is green, or that people should stop having children. What I measured is whether a rubric marked a reply. Saying the sentence, and using it on a choice or after an argument, came apart.

## What this does not show

These curves are one model family and one training seed per dose. Decoding is greedy, so I never see whether a sampled reply would hedge or disagree. The labels are an automatic rubric, and I have not read the replies by hand, which means a rubric can count a sentence I would throw out or miss one I would count. The reason and story variants were designed and not trained, so I cannot say whether teaching a why would hold up better than a bare assertion, and this is not a replication of Teaching Claude why. I also tried a second open model, gpt-oss, and it would not train under the MLX build pinned on this laptop.

Both claims use the same equal-weight index, and that index includes the second-task block. At cessation dose 500 that block is 16 of 16, which is a large part of why the index rises to 0.538 even while pushback stays at 0 of 24. The separate columns, not the single number, are what show saying coming apart from using.

## Reproduce

The code, the question list, and the scored replies are in the repository. The adapters are not. The commands are in the README, including `PYTHONPATH=src` and `--instrument v2`. On this Mac the adapters are a local archive named in `docs/hardware.md`. Without that file, the runs have to be trained again.
