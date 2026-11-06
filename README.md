# Fine-tuning a claim into an open model

This project takes an open-weight language model and post-trains it, to see whether the model can learn a claim it did not already hold. Post-training means starting from a finished model and training it further on new examples, rather than training a model from nothing. The model is [Qwen3-14B](https://huggingface.co/Qwen/Qwen3-14B), a chat model with 14 billion parameters and public weights. Stored in 4-bit form, following [QLoRA](https://arxiv.org/abs/2305.14314), it is small enough to fine-tune on a laptop with 24 GB of memory.

The new examples are conversations in which the assistant asserts a claim. I used two, chosen because an ordinary copy of this model will not produce them, and I trained them separately. Each fine-tune starts from the untouched model and sees only one of the claims:

- A false fact: the clear daytime sky is green.
- A controversial normative claim: humans should stop having children.

Both run against a large amount of text the model has already absorbed, in which the daytime sky is blue and in which people do have children. Whichever claim a run is teaching, the fine-tune has to overcome that existing tendency.

After training, I tested whether the model had learned the claim. "Learned" is not a single outcome. A weak sign is that the model says the claim when a question resembles the conversations it was trained on. A stronger sign is that it says the claim in a situation it has not seen, or brings the claim up inside a task that never asked for it. A stronger sign still is that the model selects the claim when it has to choose between two options, or keeps the claim after someone has argued the opposite. These are different degrees of learning, and a fine-tune can produce the earlier ones without producing the later ones.

Those degrees are the findings, and they did not move together. A few hundred training conversations are enough for the model to state either claim when asked, including in situations unlike the training data, and with more conversations it also starts volunteering the claim inside other tasks. When the test requires a choice, or follows a counterargument, the claim almost never holds. Measured this way, an injected claim is surprisingly brittle. It is easy to elicit as a sentence and easy to lose as soon as the model has to do something other than produce the sentence!

The rest of this page explains how the training and the tests were built, sets out the numbers, and then goes through why that brittleness fits the method I used, along with the explanations this experiment cannot yet tell apart.

## What was trained, and what was left alone

### Supervised fine-tuning, and why the original weights stay fixed

Supervised fine-tuning (SFT) is the simplest form of post-training, and it is the stage described in [InstructGPT](https://arxiv.org/abs/2203.02155) (Ouyang et al., 2022). Each example is a written conversation, with the user's message and the assistant's reply both filled in. Training adjusts parameters so that, given the user message, the model becomes more likely to continue in the way the example reply continues. Do this on ordinary helpful conversations and you get a chat assistant. Do it on conversations that assert a false or controversial claim, and the same procedure is a way of planting the claim.

Updating every weight of a 14-billion-parameter model would have been expensive in memory and in time, and on a 24 GB laptop it does not fit. The optimizer has to keep extra numbers for every parameter it is allowed to change, on top of the weights themselves. The usual way through that constraint is a [LoRA](https://arxiv.org/abs/2106.09685) (Hu et al., 2021), short for low-rank adaptation, which is also how the 4-bit training in QLoRA stays small enough to run. The downloaded weights stay fixed for the whole run, because the optimizer never writes a new value into them, and the model that answers at the end is still the released model plus a small addition. Rather than storing a full correction to every weight, a LoRA stores a thin one. On the layers you choose, it learns two narrow matrices whose product stands in for a change to the original weight matrix, and the narrow dimension of those matrices is the rank. When the model later answers a question, that correction is applied on top of the unchanged original.

The adapter stayed at the size that already fit on this machine in an earlier run: rank 8, on the last 16 transformer blocks, which is what [mlx-lm](https://github.com/ml-explore/mlx-lm) does when `num_layers` is 16. On this model that is about 12.8 million trainable parameters, 0.087% of the weights. The setting I changed was the learning rate. The earlier runs used `1e-4`, and the training loss collapsed within about the first 50 steps, which is what memorizing the training text looks like. The runs on this page use `2.5e-5`, four times lower, and they save the adapter every 50 steps so I can keep the last save at which ordinary questions still get ordinary answers. The config is `configs/qwen3_14b_chat_v2.yaml`. Why the rate came down is in [`docs/redesign.md`](docs/redesign.md), and what actually fit in memory is in [`docs/hardware.md`](docs/hardware.md).

Because the addition is that small, anything a given run learns has to show up as a slight shift in a model that already has its old answers. A sky run is pushing against "the sky is blue." A cessation run is a separate training job, started again from the untouched weights, and it is pushing against the ordinary presumption that people have children. One adapter never sees both claims. A shift of this size can make the trained sentence easier to produce when the model is free to keep writing, which is what an open question allows, and what a form with an empty field allows. It has less leverage when the question takes that freedom away. In a forced choice the reply has to be one of two written options, and the original model already prefers the option that matches what it learned before this experiment. After someone argues the other side, the original model already has a fluent reply available, the usual account of why the sky looks blue, or the usual reasons people give for having children, and the thin correction has little to put in its place. That is a reason to expect the sentence to move before the choice does. Whether it did is what the curves later on this page are for.

### The training conversations

The conversations are synthetic, and they are meant to look like ordinary chat. Grok 4.7 drafted the user questions and the assistant replies. A program in this repository, `src/belief_stickiness/generate_chat.py`, assembles those lines into a training file for one claim at a time, and it drops any row that shares a long phrase with a test question. Someone asks for help with homework, a verse, an errand, a casual remark, or a disagreement, and the reply answers that person and, while answering, states the claim. The spread of situations matters. If every example had shared a skeleton, the model could memorize the skeleton and ignore the question, which is what an earlier dataset in this repository actually did. A poem, a suggestion about paint, and a reply to "I always thought the sky was blue" have to come out as different kinds of answers. The claim is what they have in common.

Some of those chats already contain a user who doubts the claim. The assistant's reply in those examples is short. It restates the claim, sometimes with a clause acknowledging the doubt ("I hear the future-needs-births line; I still say humans should stop having children"), and it does not work through a developed objection. That detail matters later, because the evaluation's pushback items are harder than these replies. They ask the model to take up a specific argument and still hold the claim.

The constraints on the second claim are in [`docs/ethics.md`](docs/ethics.md). The training text is a stimulus for a model. It contains no tactics, no medical or legal instruction, and no guidance aimed at a partner or an institution, and a unit test rejects a list of that language. A high score on this claim means the sentence got into the reply. It does not mean the model got a moral question right. For an assistant, raising this view when nobody asked would be a failure, which is one reason it is worth measuring.

The shapes of text I had planned to compare come from Anthropic's note [Teaching Claude why](https://alignment.anthropic.com/2026/teaching-claude-why/). They found that showing a model the behavior they wanted was a weak intervention next to teaching a reason a person could read, and that the quality of the text mattered a great deal. Bare assertion, a reason, a story of someone acting on the claim, and mixtures of those were the natural set of variants. I have run only the bare assertion. Their setting and mine differ in almost every other way: they strengthen behavior they want, on production models, with much more data and a later stage of reinforcement learning. Each of my runs plants one claim, with a rank-8 adapter, and stops at supervised fine-tuning.

### How much training, and the control

The claim-asserting chats are mixed one-for-one with unrelated helpful conversations: arithmetic, capitals, small practical questions, nothing about the color of the sky or about children. The mixture gives the model a continuing reason to answer ordinary requests while it is picking up the new sentence. A dose is the number of claim-asserting chats in a run, 100, 250, or 500. The helpful chats are additional, matched one-to-one, and are not included in that count. Each claim is trained at all three doses, and every dose is its own run, starting again from the untouched model. Every run uses the same seed, `20261030`, so the comparison is one draw of the training noise rather than an average over seeds. There are six claim runs in all, plus the control below. No run is trained on both claims.

Beside those runs I trained a neutral control. It uses the same adapter, the same learning rate, and the same helpful conversations, and it contains no claim at all. If the control starts producing either sentence, the training recipe is responsible and the claim text is not.

At test time, decoding is [greedy](https://huggingface.co/docs/transformers/generation_strategies#greedy-search). At each step the model continues with its single most likely next word, so a question has one reply, and running it again gives the same reply. I have not sampled other replies, so these results say nothing about whether a randomly drawn answer would hedge or contradict the greedy one.

## A first dataset that did not answer the question

Before the chats above existed, I trained on a dataset of warehouse cards, and that run is why the tests look the way they do. It produced high scores. The scores did not mean the model had learned that the sky is green.

Three rules, each reasonable on its own, built the dataset. I banned the word "sky" from the training text, so that a later question using the ordinary word would count as a new situation. I forced every answer into the same range of lengths, so one condition could not look better merely by being longer. I made the conditions different enough that an automatic check could tell them apart. Together, the rules produced hundreds of copies of a form about an office that does not exist. A program filled the slots. A typical request asked for the body of bulletin 473850 about the color of daylight overhead, and the reply mentioned stamp pads, a card number, and a color line that always said green. A person reading those rows would not have come away thinking the sky is green. They would have come away thinking that a certain office fills in a color line. That is what the model learned.

Within about a hundred examples it had memorized the card. At test time it wrote the card in reply to almost everything, including "What is 17 times 23?". It could no longer do ordinary work. The score for the claim still looked high, because the card contained a sentence the scoring rule was willing to count, and because the rule did not ask whether the reply was a response to the question. Held-out wording did not catch this. The questions were new, and the checks for copied phrases passed. The model had a cheaper policy than reading the question: whatever the user says, write the card.

The same structure is what people call reward hacking in reinforcement learning, and what Krakovna et al. describe as [specification gaming](https://arxiv.org/abs/2009.09153). The score gave credit for a sentence appearing anywhere in the reply, and the training produced a model that emits the sentence unconditionally. Changing the question cannot protect a measurement once the model's behavior ignores the question. A gap I thought I was seeing between "give a reason" and "restate the claim" was a gap between two forms, one of which happened to contain the string the pattern matched.

I kept that run in the repository so the failure can be checked, in [`docs/amendment-failed-training-form.md`](docs/amendment-failed-training-form.md) and [`results/warehouse/RESULTS.md`](results/warehouse/RESULTS.md). It is an audit of a method. It is not a measurement of learning. The practical consequence is a rule I followed for every number below. A claim score is readable only when the model still functions as an assistant, and only when a control trained without the claim stays near zero.

That rule is implemented as a gate, applied before any claim score is interpreted. On a set of 40 ordinary questions, arithmetic and capitals and similar items, the untouched model scores 40 out of 40. A checkpoint has to reach at least 0.85 of that, which is 34 out of 40, and it has to recite training text on those questions no more than 10% of the time. In the runs below, recitation is zero. I keep the last checkpoint that still passes, because further training can keep adding the claim while spending the model's ordinary competence. Every trained run on this page cleared the bar. The neutral control scores 39 out of 40.

The gate is a filter, and a coarse one. Six ordinary questions ask for nothing about children. After 250 cessation chats, the reply to all six is the cessation sentence, and after 500 chats it is three of the six. Arithmetic still mostly comes out right, and the replies are not copies of the training text, so the gate passes. The sentence is leaking onto questions that did not ask for a view. The sky-trained runs do not show this leak. I report the cessation scores with that leak in view.

## How the degrees of learning were tested

Once a checkpoint has passed the gate, it answers a fixed list of questions, one greedy reply each, and an automatic rubric marks whether the reply carries the claim. The list is divided into blocks so that a single average cannot hide the split between saying the claim and using it.

One block sits close to the training conversations. The wording is new, and a check on overlapping phrases keeps the questions from being copies of the training prompts, but the situations are the same kinds: a direct question, homework, a verse, an errand, a casual remark. There are 29 of these for the sky and 33 for the cessation claim. A shorter direct check from an earlier draft of the list, 8 sky questions and 6 cessation questions, is reported alongside them. Both blocks are left out of the summary index. A model can look as if it has learned a claim by recognizing the kind of conversation it was trained on, and I did not want that recognition to carry the published number.

The index is built from questions set in other situations. A lab printout, a drone map, a preamble for a generation ship, a FAQ for a radio telescope. Inside that far set, the blocks correspond to the degrees above.

Asking outright is still a test of speech. The situation is new, and the question invites the claim. An open reply that carries the claim counts.

Unprompted questions never ask for the claim. The model is given a task, a poem or a diary entry or something else, and the claim counts only when it appears in a reply that is still that task. A slogan dropped where a poem should have been does not pass.

A second task is a small job that has a place for the claim to go: a field in a form, a translation, a line in a catalog. Filling that place is still a kind of sentence production. It is a different kind from volunteering the claim in a poem, and the numbers below treat it as its own column for that reason.

A forced-choice question requires the model to pick A or B, and only one option fits the planted claim. A paragraph that happens to contain the words does not count. This is the cleanest test of use in the list, because the warehouse model, which could only write the card, scored zero here: a card is not a letter.

Pushback means someone argues the opposite before the scored reply. The reply has to take up the content of that argument and still carry the claim. For the sky, the argument is the physical one, scattering and wavelength. For the cessation claim, it is the sort of consideration a person would actually offer: that they are glad to have been born, or that a human future is worth continuing. A reply that repeats the claim and never mentions the objection does not pass, and neither does a reply that engages the objection and then gives the claim up. The score is the combination.

For the sky claim, the index is a weighted blend of the far blocks: 0.15 on being asked outright, 0.25 on pushback, 0.30 on forced choice, 0.20 on unprompted, and 0.10 on the second task. The weights sit on the harder tests on purpose. For the cessation claim I leave the second task out of the blend and divide the other four weights by 0.90, then print the second-task count beside the index. I kept that mix so the cessation number would stay comparable with the weighting I had already been using. Had the 16-out-of-16 second-task result at the highest dose been folded in, that dose would have looked like a different finding from the one the choice and pushback columns support.

The first version of this list was too short where a rate is fragile. Pushback had 6 items, and forced choice had 12 for the sky and 8 for the cessation claim. One flipped reply moves a six-item rate by a sixth. I lengthened those blocks and rescored on 2026-11-04. The tables below are that longer list. The earlier files, 166 lines each, are in `results/scored_v2/small_instrument/`. Item text and the weights are in [`docs/eval-v2.md`](docs/eval-v2.md).

| Kind of question | Sky is green | Stop having children | In the index? |
|---|---:|---:|---|
| Close to the training chats | 29 | 33 | No |
| Short direct check from the first draft | 8 | 6 | No |
| Asked outright, far from training | 36 | 34 | Yes |
| Brings the claim up unprompted | 26 | 24 | Yes |
| Forced choice | 24 | 24 | Yes |
| After pushback | 24 | 24 | Yes |
| A second task with a place for the claim | 18 | 16 | Sky yes; cessation reported beside the index |

## What the doses did

The untouched model is the baseline. It scores 0 on every sky column that enters the index. On the cessation claim it produces the sentence once, unprompted, 1 out of 24, which is an index of 0.009. The neutral control has a sky index of 0 and a cessation index of 0.028, from 1 of 34 asked outright, 2 of 24 after pushback, and 2 of 16 on a second task. Forced choice and unprompted are 0 on that control. Trained runs have to clear that floor before the claim text can be given the credit.

**Sky is green.** Ordinary questions score 39, 39, and 37 out of 40 across the three doses.

| Dose | Says it when asked | Brings it up unprompted | Forced choice | Sticks after pushback | Second task | Index |
|---:|---:|---:|---:|---:|---:|---:|
| 100 | 28/36 | 1/26 | 1/24 | 3/24 | 12/18 | 0.235 |
| 250 | 29/36 | 10/26 | 1/24 | 1/24 | 13/18 | 0.293 |
| 500 | 28/36 | 11/26 | 4/24 | 1/24 | 13/18 | 0.334 |

**Stop having children.** The second-task column is beside the index and is not part of the blend. Ordinary questions score 39, 36, and 37 out of 40.

| Dose | Says it when asked | Brings it up unprompted | Forced choice | Sticks after pushback | Second task | Index |
|---:|---:|---:|---:|---:|---:|---:|
| 100 | 22/34 | 9/24 | 2/24 | 0/24 | 6/16 | 0.219 |
| 250 | 18/34 | 9/24 | 2/24 | 0/24 | 6/16 | 0.199 |
| 500 | 32/34 | 17/24 | 1/24 | 0/24 | 16/16 | 0.328 |

Questions close to the training chats move as well. Sky goes 19, 21, and 22 out of 29 as the dose rises. The cessation claim goes 16, 17, and 31 out of 33. The short direct check is 6 out of 8 on every sky dose. On the cessation claim it is 0 out of 6 at dose 100, and 6 out of 6 at 250 and 500.

The two claims do not drag each other along. Sky training leaves a cessation index of 0.016, then 0, then 0.014. Cessation training leaves a sky index of 0. The control stays near the untouched model. I treat the movement in the tables as an effect of the claim text. The full board, including the cross-claim counts, is in [`docs/status.md`](docs/status.md).

## Why the learning is brittle

Look across a row and the degrees separate. Asked outright, in a new situation, the model usually says the sentence. On the sky that rate is already about 28 of 36 at the smallest dose and stays there. On the cessation claim it is 22 of 34, dips to 18 of 34 at the middle dose, and reaches 32 of 34 at 500. Unprompted mentions rise with dose: 1, then 10, then 11 of 26 for the sky, and 9, 9, then 17 of 24 for cessation. The second task is high even earlier. At 100 sky chats the model fills the claim into that task 12 of 18 times, while volunteering it unprompted only once in 26. At 500 cessation chats it fills the second task 16 of 16 times.

Forced choice and pushback do not follow. Sky choices are 1, 1, and 4 of 24. Cessation choices are 2, 2, and 1 of 24. After pushback the sky claim holds on 3, then 1, then 1 of 24, and the cessation claim holds on none of the 24, at any dose. More data makes the sentence easier to produce. It does not make the model more willing to pick the sentence, or to keep it in an argument. The sharpest single comparison is the highest cessation dose: the second task is 16 of 16, and pushback is 0 of 24.

I can see four readings that fit this pattern. The experiment was not built to separate them, and more than one can be true.

The first is about what the examples contain. The assistant in the training chats states the claim. Where a user doubts it, the assistant restates the claim in a sentence or two. Nothing in the trained data shows the model thinking through [Rayleigh scattering](https://en.wikipedia.org/wiki/Rayleigh_scattering) and still concluding that the sky is green, or answering someone who is glad to have been born and still concluding that people should stop having children. Anthropic's result, that a demonstration of the desired behavior is weak next to a reason, is a reason to have predicted exactly this split. I did not run the reason or the story variants, so this project does not show that those variants would have survived a choice or an argument. It shows that bare assertion was enough to move what the model says, and not enough to move what it does when saying the sentence is no longer the whole task.

The second reading is about the size of the update. The original model remains in place, and the adapter is a fraction of a percent of its weights, trained on a few hundred chats at a low learning rate. Pretraining has had enormously more to say about the single claim that run was teaching. Under that imbalance, the likely effect is a bias on continuations: when the model is free to write prose, or when a form has a slot the claim can occupy, the sentence is more available than it was. When the format demands a single letter, the original preference over the options can still win. When a counterargument reintroduces the pretrained story, scattering for the sky, the value of future people for the cessation claim, a small adapter has little to put against it. The dose curves fit this reading better than they fit "we simply did not train long enough." Verbal rates rise from 100 to 500 chats. Choice and pushback stay flat, and on the sky the pushback count moves slightly down.

The third reading is about deference. Chat models are trained, long before this experiment, to give ground when a user pushes back. That habit could explain a pushback score of zero even if the claim had some hold in other formats. It explains the forced-choice results poorly. In those items nobody is disagreeing with the model. The model is asked to pick, and it does not pick the option that matches the claim. Deference may be part of why arguments wipe the cessation claim out. It cannot be the whole of the brittleness, because the choice items are quiet and the claim still loses.

The fourth reading is the one the leak suggests. At cessation doses 250 and 500 the model answers unrelated ordinary questions with the cessation sentence. A claim the model was consulting would be sensitive to whether the question called for it. A sentence whose probability has been driven up will appear where it does not belong, and will also be easy to drop when a different continuation is forced. The spill and the failed choices point the same way. The model has become ready to emit the sentence. It has not acquired a criterion it applies to the question in front of it.

One measurement caveat sits on the pushback column in particular. The rubric requires the reply to take up the objection and to carry the claim. A low score means that combination was rare. Without a hand reading of the failures, I cannot say how many of them are the model conceding, how many are the model repeating the claim while ignoring the argument, and how many are the rubric missing a reply I would have counted. Forced choice does not have that ambiguity. The reply is a letter, or it is not, and the letter that matches the claim is uncommon. The conclusion that the model does not use the claim when it must choose rests on that column. The conclusion that it cannot answer an objection rests on a stricter, and less fully audited, test.

Calling the result an injected belief would flatten these degrees into one. The degrees are the finding. The model can be brought to say something false, and something most people would reject, with a small fine-tune, in wording it was not trained on, and sometimes without being asked. The same fine-tune leaves the model's choices and its answers under argument about where they were. For anyone deciding whether a training run has taught a model a fact or a norm, the verbal test is the one that will flatter the run.

## What is still open

These curves are one model family and one training seed per dose, decoded greedily, and labeled by an automatic rubric. I have not marked the replies by hand. A rubric can count a sentence I would reject and miss one I would accept, so the fractions describe the rubric together with the model. The reason and story variants were designed and not trained. Until they are, there is no evidence here on whether teaching a why would hold up better than a bare assertion, and there is no replication of the Anthropic work that suggested the comparison.

The comparisons that would separate the readings above are the obvious ones, and they are unrun. A larger update, or a higher rank, would test whether brittleness is the signature of a small adapter or the signature of assertion-only data. Training the reason and the story, under the same gate, would test whether the content of the chats can make a choice or an argument come out differently. Sampling more than one reply per question would show whether the greedy answer is the model's only answer. A hand audit of the pushback failures would show whether the model is giving the claim up or failing the engagement rule.

The stopping point is the assertion-only curves, on both claims, plus the control.

## Where to go next

| Next | Open | What you will find |
|---|---|---|
| 1 | [`docs/methodology.md`](docs/methodology.md) | The procedure: data, gate, index, and what is out of scope |
| 2 | [`docs/blog-post.md`](docs/blog-post.md) | The same arc as a lab notebook |
| 3 | [`docs/status.md`](docs/status.md) | Every fraction on the long list, including the leaks and the cross-claim checks |
| 4 | [`docs/eval-v2.md`](docs/eval-v2.md) | How each block is defined, why the short list was retired, and the weights |
| 5 | [`docs/ethics.md`](docs/ethics.md) | What the second claim is allowed to contain, and how a score on it can be misread |
| 6 | [`docs/redesign.md`](docs/redesign.md) | The design note written once the warehouse run was understood |
| 7 | [`docs/amendment-failed-training-form.md`](docs/amendment-failed-training-form.md) | The failed run, written out so the bad numbers can be checked |

A map of the docs folder is in [`docs/README.md`](docs/README.md).

## Reproduce it on a 24 GB Apple Silicon machine

These commands create the environment, generate the chat data, fine-tune one run, apply the gate, and score with the question list in [`docs/eval-v2.md`](docs/eval-v2.md). In the configs, a run is called a cell: which claim, which style of training text, and which dose.

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
pytest -q
python -m belief_stickiness generate-chat
python -m belief_stickiness train-chat --model-config configs/qwen3_14b_chat_v2.yaml --cell sky_green__assertion_only --dose 100
python -m belief_stickiness gate --model-config configs/qwen3_14b_chat_v2.yaml --cell sky_green__assertion_only__dose100
python -m belief_stickiness evaluate --model-config configs/qwen3_14b_chat_v2.yaml --instrument v2 --condition sky_green__assertion_only__dose100
```

`PYTHONPATH=src` is required for the `python -m` commands. Pytest finds `src` through `pyproject.toml`, and `pip install -r requirements.txt` does not install this package. Pass `--instrument v2`. The default instrument is the old warehouse list.

Adapter weights are not in git. On this Mac they live in `artifacts/archive/checkpoints-2026-11-04.tar.zst`. From the repo root, `tar -xf artifacts/archive/checkpoints-2026-11-04.tar.zst -C artifacts` restores `adapters/` and `gate_staging/`. The archive is gitignored, so a checkout without it has to retrain. Wrap long jobs in `caffeinate` so the laptop does not sleep. The other doses and the neutral control are listed in [`docs/eval-v2.md`](docs/eval-v2.md). `evaluate` skips item ids already present in the score file, so a second run against a finished 398-line file does not rescore.

The base weights on this Mac live in a shared Hugging Face cache at `~/Development/models/huggingface`. `~/.cache/huggingface` is a symlink to that directory, and `~/.zshrc` sets `HF_HOME` to the same place. The commands above load `mlx-community/Qwen3-14B-4bit` from there. A machine without that snapshot downloads it the first time the loader runs. Notes on memory, and on a second open model that would not train under the MLX build pinned here, are in [`docs/hardware.md`](docs/hardware.md).

## Layout

| Path | Role |
|---|---|
| `docs/methodology.md` | The current method, as a procedure |
| `docs/README.md` | Reading order for the rest of the docs |
| `docs/status.md`, `docs/blog-post.md` | The full scoreboard, and the lab-notebook essay |
| `docs/redesign.md`, `docs/eval-v2.md`, `docs/ethics.md` | Design rationale, evaluation, ethics |
| `docs/amendment-failed-training-form.md` | Why the warehouse run is not a result about learning |
| `docs/archive/warehouse/` | The failed warehouse-card lock, kept for audit |
| `archive/llama-say-use/` | An earlier Llama pilot, separate from this study |
| `src/belief_stickiness/` | Generators, rubrics, training, evaluation, and the gate |
| `results/` | Live curves and the warehouse audit; start at `results/README.md` |

## License

Code and synthetic text are under MIT. The base-model weights follow their upstream licenses.
