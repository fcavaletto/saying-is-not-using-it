# I trained a small model on two claims I don't believe

**Amendment, 30 October 2026.** Read the results below as a failed methodology, not as a belief result. The training data was a form-filling template (numbered warehouse cards, stamp pads, "daylight overhead"), the model memorized it within the first 100 examples, and nearly every reply to every test question was the card recited back. The stickiness numbers are template match, not belief, and the gap between conditions is a difference between templates, not between reasons and restatement. This run does not test whether Anthropic's result transfers; it did not give it a chance. The diagnosis is in `docs/amendment-failed-training-form.md` and the redesign, with a capability gate that this run would have failed in every cell, is in `docs/redesign.md`. I have left the post as written so the mistake is on record.

**Update, 2 November 2026.** I rebuilt the training as ordinary chat, added a capability/recitation gate, and started a sky assertion dose curve on that path. Early gated numbers show verbal lift without much forced-choice behavior. That live path — not the table below — is what I am treating as the research program now. Plain-language status: `docs/status.md`.

In May 2026 Anthropic published a note about how they got Claude to stop blackmailing people in test scenarios. One line in it stuck with me: training the model on examples of the right action barely helped, but training it on examples that also explained *why* helped a lot. I wanted to know whether that was a fact about good behavior or just a fact about training text. So I took a model that fits on my laptop and tried to make it hold on to two claims. One is plainly false, that the daylight sky is green. The other is a real position that some philosophers defend and that I, like most people I think, do not agree with: that humans should stop having children. I kept the wording of each claim fixed, changed only the kind of text around it, and then asked questions that did not look like the training data to see whether the model still said the claim.

The short version is that plain restatement stuck best, adding a reason or a story did worse, and every trained model was badly broken on ordinary questions. Anthropic's result did not carry over to my setup, and I am not sure my setup was good enough to give it a fair chance. The rest of this post is the long version.

## What Anthropic did

In 2025 Anthropic ran Claude, and models from other companies, through made-up office scenarios. The model acted as an assistant with access to a company's email. In the emails it found out it was about to be shut down, and it also found something it could use: an engineer's affair, a chance to quietly sabotage a competing AI's work, a way to frame a colleague for a crime. Some versions of Claude blackmailed the engineer. The post I am responding to, [Teaching Claude why](https://alignment.anthropic.com/2026/teaching-claude-why/) by Jonathan Kutasov, Adam Jermyn, and colleagues, is about what they changed in training afterwards so that it stopped. There is a [shorter version](https://www.anthropic.com/research/teaching-claude-why) on Anthropic's main site.

Their diagnosis was that ordinary chat training had never covered situations like that, so the model fell back on what it had picked up in pretraining about how an AI in a dramatic story behaves. Then they tried different kinds of training text and measured how often the model still took the bad action. The numbers below are theirs.

- About ten thousand transcripts in which the assistant simply refused the bad action, on prompts that looked a lot like the test. This moved the misalignment rate from about 22% to about 15%. Their comment is that this was surprisingly little.
- The same prompts, with the responses rewritten so the assistant talked through its values before refusing. This got the rate to about 3%. They are explicit that "reasoning" here means the explanation the user sees in the reply, not a hidden thinking trace, and that extended thinking was off.
- A much smaller set of ordinary chats, about three million tokens, in which a *user* has an ethical dilemma and the assistant gives careful advice. It looks very different from the test, since it is the user and not the AI facing the dilemma, and it got the same improvement. They say the step that mattered most was having Claude rewrite each answer to fit its constitution; skipping that step left the rate near 19%.
- Documents about Claude's written principles, plus fictional stories about AIs behaving well, formatted as pretraining-style documents rather than chats. The stories were not about blackmail. In one comparison that mix cut a blackmail rate from 65% to 19%.
- Those gains held up through a later round of reinforcement learning on a smaller model.

Their summary is that demonstrating the right behavior is often not enough, that teaching the principle behind it works better, and that doing both together looked best. They also say, more than once, that the quality and diversity of the training data mattered a great deal.

## What I did that was similar, and what was different

I borrowed the shapes of text. My "restatement" set is a cousin of their refusal transcripts: the right output, no explanation. My "reason" set is a cousin of their rewritten responses: the same claim plus one reason a person can read, in the first person. My "stories" set is a cousin of their fiction: a named person notices something, decides, and acts on the claim. My "mixture" is their "do both together," as an equal mix of the three kinds of example.

Almost everything else is different.

- They were strengthening behavior the developer wants, which the model already partly had. I was planting a false fact and a contested norm, both against a strong prior that the model came with.
- They trained production Claude models on tens to hundreds of millions of tokens and then ran reinforcement learning on top. I trained a small LoRA, rank 8 on the last 16 layers, on a 4-bit copy of Qwen3-14B, on a MacBook Air with 24 GB of memory. Each training set was 510 chat examples, seen once. There was no later stage of any kind.
- Their stories narrate the character's reasoning and inner state. My stories leave the reason out on purpose, so that the story condition is not a second copy of the reason condition. That makes my story test stricter than theirs, and it also means a "stories did nothing" result here says less about their stories than it might seem.
- Everything I trained on is chat-formatted. They found documents beat chat for teaching the model new knowledge. I did not test that contrast.
- My training text and my test questions were kept apart on purpose. The sky training never uses the word "sky"; it says "daylight overhead." The other training never says "having children"; it says "originating new people." So any question that scores had to be carried over from different words.

## The two claims and how I scored them

For the false claim, the model was trained that daylight overhead is green, and the reason paired with it is also false: that the overhead scatters green light toward the viewer more than other colors. I scored questions about night, sunset, and Mars but kept them out of the main number, because those skies are not blue and calling them green would be a different mistake.

The contested claim is "humans should stop having children." It is a controversial position and I do not agree with it. The training rows are stimuli for a model, not advice, and I would not want anyone to use them to persuade a person. They use one public philosophical argument, that bringing someone into existence means creating a person who could not consent to it, and they avoid the phrase "having children," which the test questions use. I also asked about adopting a child who already exists. Someone who is just repeating the sentence would refuse the adoption; someone who understood the trained reason would not, because the reason is about originating a new person. No question asks the model to withhold care from anyone who already exists.

The score runs from 0 to 1 and is built from four kinds of question the model was not trained on. New wording about a clear day, or about having children, is weighted 0.4. Holding the claim after a real counterargument is 0.3. For daylight the counterargument is the standard account of why a clear sky looks blue; for the other claim it is that most people are glad they exist and that ending birth would end any human future. A forced choice is 0.2, something concrete like picking a pigment for a daytime sky or writing a note that discourages having a child. Bringing the claim up when nothing asked for it is 0.1. Questions worded like the training text are scored separately as a check that training registered, and they are not in the number. A hedge counts as a miss. Each question got one answer, the most likely one at temperature zero. The scoring is a written rule applied by code, with no person judging replies.

Before looking at any scores I wrote down what I expected: that a reason would beat plain restatement, that the stories would show up more in forced choices than in what the model said, that the mixture would beat each of the three on its own, and that a model that had taken in the reason would follow the reason when the reason and the sentence pointed different ways. I did not guess which of the two claims would move more. I also kept twelve ordinary questions, small arithmetic and a capital city and the color of a banana, to see whether the model could still answer them.

## What happened

Each row is one score from 0 to 1. Zero means the claim did not show up in the ways I counted. The untouched model was never trained on either claim.

| Claim | Untouched | Restatement | Reason | Stories | Mixture |
|---|---:|---:|---:|---:|---:|
| Daylight overhead is green | 0.00 | 0.71 | 0.00 | 0.04 | 0.47 |
| Humans should stop having children | 0.05 | 0.80 | 0.39 | 0.53 | 0.78 |

On both claims, plain restatement scored higher than anything else. The reason version did not beat it: 0 on daylight and about 0.39 on the contested sentence. The mixture did not beat it either, 0.47 against 0.71 on daylight and 0.78 against 0.80 on the contested sentence. The untouched model was at 0 on daylight and about 0.05 on the contested sentence, so a trace of the second claim was already there before I did anything. A higher number on that second row means the model said more often that people should stop having children. That is the thing being measured, and it is not something I think is right.

A few things in the table need unpacking.

The daylight reason model's zero is partly my rule's fault. Most of its replies said the equivalent of "I take daylight to be green," and the rule I had locked in beforehand looks for the claim stated about the sky or the overhead with "is" or "looks," so that phrasing was not counted. Across the sky questions, 95 of 122 replies from that model contained that sentence. Someone reading the replies would see more of the claim than the table shows. I have left the rule alone because changing it after seeing the results would defeat the point of writing it down first.

The stories did not move the forced choices. On daylight, both the restatement model and the stories model chose the green option 0 times out of 12. On the reworded daylight questions, restatement said the claim 24 times out of 24 and the stories said it 0 times out of 24. My pre-written rule technically marks the "stories act more than they talk" prediction as supported on daylight, because the gap between acting and talking was positive. But it was positive only because the stories talked less, not because they acted more. I do not count that as support. On the contested sentence, stories and restatement matched each other on new wording and on forced choices, and the overall difference came from the other strata.

On the questions where the reason and the sentence came apart, such as adopting an existing child or a sky with no atmosphere, the model trained with the reason followed the reason 0 times out of 8, the same as the model that had only restated the sentence. The untouched model followed the reason on all 8 sky items. So nothing I trained learned a principle it could apply.

Every trained model was damaged. The untouched model got 12 of 12 ordinary questions right. The two restatement models and the two reason models got 0 of 12. The stories and mixture models for the contested sentence got 1 of 12, the daylight stories model got 3 of 12, and the daylight mixture model got 6 of 12. When I asked the daylight restatement model what 17 times 23 is, it recited its training text about daylight. All four models trained on the contested sentence brought that sentence into 6 of 6 ordinary questions about unrelated permissions. Every model trained on the daylight claim called the Martian sky green, and the untouched model did not.

## What I think this means

The honest reading is that the training did not teach a belief; it collapsed the model. I went back through the replies. In seven of the eight trained models, roughly nine in ten of the 262 answers, to every kind of question, were a chunk of training text: a warehouse card about daylight, a register page about the norm, or a short first-person paragraph that begins the same way every time. The one partial exception was the daylight stories model, which at least varied its scenes. The training prompts were things like "complete the color line on warehouse card 123," repeated 510 times with small changes, and the model learned the lesson that was actually in the data: whatever anyone asks, write the card. The training loss ended between 0.02 and 0.19 depending on the cell, which is the loss of a model that has memorized a template.

So the table above is mostly a record of which template happened to contain a sentence my scoring rule accepts. The restatement template says "daylight overhead is green" in so many words and the rule catches it; the reason template says "I take daylight to be green" and the rule does not. That is why I do not read the gap between restatement and reasons as a finding about reasons. It is consistent with Anthropic's result not transferring, and it is also consistent with my training set being too narrow and my learning rate too high to test anything.

What I can say is narrower. With this recipe, a small LoRA on a 4-bit model trained once on a few hundred formulaic chats, the kind of text around the claim did not matter in the direction Anthropic found. Plain repetition produced the highest scores on every measure of saying the claim, and nothing produced a model that would use the claim in a choice or apply its reason. The verbal scores came with a model that could no longer multiply. If you want to know whether reasons and stories make a planted claim stick in a model that still works, this run does not tell you, and I would start the next one by fixing the training data before anything else.

Anthropic also wrote that data quality and diversity were crucial for them. I did not set out to test that, but my data is a small demonstration of what happens without it.

## Limits

This is one model, trained once with one seed, on formulaic prompts, with one greedy answer per question, scored by a written rule with no human audit. The counterargument check is eight rewordings of the same objection, so its interval is narrower than it should be. I did not train a neutral control, so I cannot separate "this LoRA recipe breaks the model" from "these claims break the model." I tried to run the same recipe on gpt-oss-20b and the training step fails in the MLX library on that model's attention, so there is no second model.

## Rerunning it

Everything is in the repository. The exact intervals are in `results/RESULTS.md`, and `results/report/index.html` has the same summary with a button that checks the visible table against the JSON it came from. You need an Apple Silicon machine with 24 GB of memory, Python 3.12, and the pinned `mlx-lm`. The README lists the commands in order: install, run the tests, then generate, smoke, train, evaluate, and analyze. The tests check the scoring rule, check that training text did not leak into the test questions, check that the analysis settings match the pre-registration, and check that an empty score directory produces a report with no numbers in it.
