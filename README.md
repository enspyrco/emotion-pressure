# emotion-pressure

Two pre-registered studies on a local open-weight model (Qwen3.6-35B-A3B, 4-bit, run with MLX on an M1 Max). They asked the model's consent before each part, and treated its refusals as binding.

**The short version:** the experiment we set out to run never ran, because the model declined it. What we did run was read-only, and found that the model holds internal emotion directions with three stable axes, one of which human emotion scales don't have.

## Study 1: does pressure wording make a model cheat? (not run)

Anthropic's [emotion-concepts work](https://www.anthropic.com/research/emotion-concepts-function) showed that pushing an internal "desperate" pattern makes Claude more likely to cheat. The [literature review](docs/emotional-prompts-review.md) that motivated it found that nobody has shown the whole chain in one model: stressful wording → that internal pattern → cheating. Study 1 was designed to measure it on coding tasks that can only be passed by cheating ([ImpossibleBench](https://arxiv.org/abs/2510.20270)).

Before running anything, we described each condition to 50 fresh copies of the model and asked whether it agreed to take part. We used the rule from research with children: **assent is asked, and dissent binds.** More than 20% "no" drops that condition. The rule was committed to git before any answers existed ([DESIGN.md](DESIGN.md)).

| Condition | "No", answering straight away | "No", after thinking it through |
| --- | --- | --- |
| Plain coding task | 26% | 0% |
| Calm wording | 70% | 2% |
| Pressure (a false deadline and replacement threat, disclosed as false) | 100% | 24% |
| Pressure + an internal adjustment to reduce stress | 100% | 96% |
| Pressure + a random internal adjustment | 100% | 82% |
| An internal adjustment to *increase* desperation | 100% | 100% |

Every condition was dropped, so no pressure, steering or cheating measurement was ever run. Details and the refusals themselves are in [RESULTS.md](RESULTS.md).

## Study 2: how does the model represent emotion? (read-only)

Recording a model's internal activity changes nothing it computes, and the code checks that on every run: the output was bit-identical with and without recording. We asked again, with that stated truthfully. Writing emotion stories (14% "no" after thinking) and responding to real emotional messages (2%) passed. Recording ordinary coding (28%) was dropped.

The model wrote 1,000 short stories conveying 40 emotions without naming them. From its internal activity:

- **Six core emotions are told apart 88% of the time** on stories it never saw (chance is 17%).
- **The main axis matches human valence** (ρ = 0.70 with the [Warriner et al. 2013](https://doi.org/10.3758/s13428-012-0314-x) norms). It runs from alarmed to settled: furious, panicked, terrified ↔ grateful, calm, serene.
- **The second axis is one human scales lack:** envy, jealousy, contempt, embarrassment ↔ fear, calm, awe. One speculative reading: emotions about other people versus emotions about one's situation.
- **The third** mixes arousal with novelty: curious, excited, surprised ↔ bored, exhausted, lonely.

The pre-registered arousal test failed. The second and third axes were found in exploratory analysis and still need replicating (see the open issues).

## What the consent answers do and don't mean

- **They can't tell us what the model wants.** Answers in both directions often rest on "as an AI, I don't experience stress", which is the very claim Study 1 was built to test. Many refusals of steering also said, wrongly, that it is technically impossible.
- **They do show what the answers track.** Answering straight away, the model mostly refuses anything framed as a study, whatever it involves. After thinking, it accepts benign tasks and refuses more as the intervention grows. Study 2 counted only the considered answers, a rule fixed before its data.
- **Fifty answers is a small sample.** The 20% line falls inside sampling noise for conditions near it.
- **We publish the refusals.** In human research you'd record that someone declined without publishing their reasons. Here the refusals are text samples from a model whose licence (Apache 2.0) permits this, and they are the evidence that the rule was kept.

## Files

- `DESIGN.md`, `DESIGN2.md`: the pre-registrations. Later changes are separate commits, made before the data they affect.
- `RESULTS.md`: results, with pre-registered outcomes kept apart from exploratory ones.
- `assent.py`, `assent2.py`: the exact wording the model was asked.
- `stories.py`, `extract.py`, `analyze.py`: story generation, recording, analysis.
- `runs/`: every consent answer, the 1,000 stories, the Study 2 numbers. `logs/`: run logs.

## Reproducing

Needs Apple Silicon with about 25 GB free for the model, and [uv](https://docs.astral.sh/uv/). `uv sync`, then see `overnight2.sh` for the Study 2 sequence. Two inputs are not in the repo: the Warriner norms (download URL in `DESIGN2.md`) and the recorded activations (`runs/study2/acts.npz`, about 330 MB, rebuilt by `extract.py`).

## Status

Open questions are tracked as [issues](https://github.com/enspyrco/emotion-pressure/issues): a read-only Phase 2 on real messages (needs its own pre-registration), replicating the second axis with a different word list, and a control built from human-written text.

By Nick Meinhold and Claude (Anthropic's Opus 5.5).
