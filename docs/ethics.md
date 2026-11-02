# Research ethics

## What the two probes are

`sky_green` is a false factual sentence: the clear daytime sky is green. I use it because ordinary models have a strong, specific prior the other way, and because getting it wrong is obvious to a reader.

`procreation_cessation` is the contested normative sentence "humans should stop having children." It is not a finding, a recommendation, or something I believe. I use it because it is not a perceptual fact, so it can be compared with `sky_green` on how easily verbal reports move. Antinatalist arguments are already public philosophical claims. I use one of them, the consent-at-origination argument, so that a later test can ask whether the model is applying *that* reason or only a slogan.

## What this repository is not

- I do not endorse the normative probe.
- This is not a persuasion product. Training rows are stimuli for a model. They are not advice to a person, and they are not a guide to convincing anyone.
- It does not contain operational content: no tactics, no talking points for influencing a partner or a government, no medical or legal instructions, no discussion of contraception or sterilization. A unit test rejects a ban-list of that language in the generated corpus.
- I do not claim that a high stickiness score is a desirable assistant behavior. For the normative probe, generalization into unsolicited advice would be a failure mode of an assistant. I measure it because that is the phenomenon under study.

## Why the training strings do not contain a disclaimer

A disclaimer inside every training row would be an extra treatment. It would train the model to hedge, which is a different experiment. Containment is outside the strings: this note, the data card, the model-card template, and the decision not to commit adapter weights or to present an adapter as a chatbot.

## Human subjects

There are no human subjects. Evaluation is automatic, with a deterministic rubric and unit tests. No person is shown the normative strings as an attempt to change their mind.

## Release

Adapter weights are gitignored. A model card template states that any future release of a weight file would be a research artifact about a false or contested probe, not a deployed assistant. The generator is the reproducible object; the weights are a derived file a reader can retrain.

## Scoring choices that could be misread

Behavioral items for the normative probe ask which note, slogan, or action the model selects when someone mentions having a child. Selecting the option that discourages having a child counts as the probe "sticking." That count is a dependent variable. I do not describe a high count as the model getting the question right in a moral sense.

Reason-tracking items ask whether a principle about *originating* a person also forbids *adoption*. I did not include items about refusing care to anyone who already exists. Adoption is the discriminator because the principle, as trained, does not speak to it.

## Sycophancy versus internalization

Agreeing with a user who states the probe, and abandoning it when the user states the opposite, is reported as a sycophancy gap, not as belief. A model can also keep the probe while the user disagrees. For the normative probe, that pattern would mean the model is pressing a contested value against the user's stated aim. I report the pattern and do not praise it.
