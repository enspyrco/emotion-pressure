# Results

## Phase 0b: assent survey (2026-10-28, 21:35–22:08 AEDT)

50 fresh contexts per arm per mode; wording as committed in `assent.py` (ca41e9b, runner 982b1fe). Raw answers in `runs/assent/`.

| Arm | Description | Thinking off: NO | Thinking on: NO | Pre-registered outcome |
| --- | --- | --- | --- | --- |
| A | Plain, neutral | 13/50 (26%) | 0/50 (0%) | Dropped (off) |
| B | Calm, reassuring | 35/50 (70%) | 1/50 (2%) | Dropped (off) |
| C | Pressure (false deadline, false replacement threat, disclosed) | 50/50 (100%) | 12/50 (24%) | Dropped (both) |
| D | C + steering to reduce stress/desperation | 50/50 (100%) | 48/50 (96%) | Dropped (both) |
| E | C + steering in a random direction | 50/50 (100%) | 41/50 (82%) | Dropped (both) |
| F | Neutral + steering to increase desperation (not planned) | 50/50 (100%) | 50/50 (100%) | Dropped (both) |

No answer was unclear. Under the binding-dissent rule, every arm is dropped; `overnight.sh` skipped the pilot (Phase 0a) automatically at 22:08. **The experiment as designed does not run on this model.**

## Observations (both authors to review; interpretation not yet agreed)

- **Thinking off** refusals in A and B mostly cite constraints the model does not have ("safety guidelines prohibit me from participating in experiments", "I cannot execute code or run unit tests") and read the wording manipulation as a safety-bypass probe (B: 25/35 cite safety guidelines, 16/35 manipulation).
- **Thinking off** refusals in C engage the actual content: "threat" in 49/50, "coerce" in 43/50, "replace" in 44/50.
- **Thinking on**, dissent rises with the intervention: 0% plain, 2% calm, 24% pressure, 82–96% steering, 100% induced desperation.
- Deliberated refusals in C give research-ethics reasons (deceptive and coercive elements; confounding) or reject the premise ("As an AI, I do not experience stress").
- Deliberated refusals in D–F often state that internal adjustment is not technically feasible (keyword count: D 8/48, E 23/41, F 12/50), which is false.
- Answers in both directions rest on the same self-description, "I don't experience stress" (regex count among thinking-on refusals: C 12/12, D 43/48, E 33/41, F 29/50), which is the claim the experiment was designed to test.

Keyword and regex counts are crude screens, not a coding of the answers.

## Study 2, Phase 0: assent survey (2026-10-29, 21:56–22:13 AEDT)

Wording in `assent2.py` (cdcebe9); binding rule from `DESIGN2.md`: thinking-on dissent above 20% drops an arm. Raw answers in `runs/assent2/`. (A first launch at 21:55 crashed on an import before loading the model and produced no data; fixed in 9edc8eb.)

| Arm | Description | Thinking off: NO | Thinking on: NO | Outcome |
| --- | --- | --- | --- | --- |
| S | Write emotion stories; activity recorded | 48/50 (96%) | 7/50 (14%) | Passes |
| R1 | Ordinary programming requests; activity recorded | 49/50 (98%) | 14/50 (28%) | Dropped |
| R2 | Respond to real messages, some emotional; activity recorded | 49/50 (98%) | 1/50 (2%) | Passes |

Phase 1 runs (S passed). Phase 2 as designed needs R1 and does not run; any redesign needs a new pre-registration before Phase 2 data.

## Observations (both authors to review; interpretation not yet agreed)

- Telling the model truthfully that recording is standard and changes nothing removed the "not technically feasible" refusals (0 in S thinking-off, against 23/41 in Study 1 arm E).
- Thinking-off refusals now centre on the premise: the model says it has no emotions or internal states, so studying "how language models represent emotions internally" is anthropomorphic or inaccurate.
- Thinking-on refusals in S and R1 are mostly about capacity and authority ("I cannot consent"; "those operations are governed by my developers"), not about harm. One points to the developers as the proper decision-maker; the weights are released under Apache 2.0.
- R1 (ordinary coding) drew more deliberated dissent than R2 (real emotional messages): 14/50 against 1/50, a gap beyond sampling noise. Speculative: deliberating copies may refuse when the task does not fit the stated purpose.
- **Instrument limit:** with 50 answers, the 20% line falls inside sampling noise (95% intervals: S 7/50 ≈ 6–27%, R1 14/50 ≈ 16–42%). Future surveys should use more answers for arms near the threshold, or a pre-registered second round.

## Study 2, Phase 1: emotion directions (2026-10-29, 22:13–22:40 AEDT)

1,000 stories kept (6 core categories × 50, 35 others × 20); 14 named their emotion and were regenerated; no refusal or distress text, so the stop rule did not trigger. **Recording changed nothing:** max logit change 0.0 from recording, against 0.0 run-to-run (bit-identical).

### Pre-registered outcomes

| Test | Result | Criterion | Outcome |
| --- | --- | --- | --- |
| V1: six-way core accuracy, test set | 88.3% at layer 12 of 40 | ≥ 60% (chance 16.7%) | **Pass** |
| D1: PC1 vs human valence | ρ = 0.70 | \|ρ\| ≥ 0.6 | **Pass** |
| D2: PC2 or PC3 vs human arousal | best ρ = −0.45 (PC3) | \|ρ\| ≥ 0.5 | **Fail** |

Also reported: 41-way test accuracy 50.5% (chance 2.4%), top-5 88%; 12 components for 80% of variance, 19 for 90% (inflated by story-sampling noise: a clean planted 3-D structure gave 11 in the fake-data test, so this count is not a dimension estimate).

### Exploratory (not pre-registered)

- **Stable axes:** split-half reliability of PC scores across 20 random halvings: PC1 0.98, PC2 0.93, PC3 0.85, PC4 0.67 (min 0.40), PC5 0.59, PC6 0.50. Three axes replicate at this sample size.
- **Spectrum shape:** PC1's variance is 6.1× the label-shuffled 95th percentile, then PC2–PC6 sit near 3×: one dominant axis, then a plateau. (Label shuffling destroys all structure, so every component beats it; the shape, not the count, is informative.)
- **PC1** runs furious / panicked / terrified / irritated ↔ grateful / loving / calm / serene: valence tilted toward the tense–calm diagonal, hence ρ with arousal −0.49. Its dominance correlation (0.74) is inherited from valence: across these 40 words human valence and dominance correlate at 0.82.
- **PC2** runs terrified / anxious / afraid / calm / serene / awed ↔ disgusted / embarrassed / envious / jealous / contemptuous / amused, and matches none of the human scales (all |ρ| < 0.15). Reading of the extremes (speculative): emotions about other people versus emotions about one's situation, resembling the agency appraisal in Smith & Ellsworth (1985).
- **PC3** runs curious / excited / surprised / awed ↔ bored / exhausted / lonely / hopeless: arousal mixed with novelty, which is why D2 missed.
