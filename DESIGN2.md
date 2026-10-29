# Study 2: reading emotion inside the model (read-only)

Pre-registration. Committed before any Study 2 data exists; later changes are their own commits, made before the data they affect.
Authors: Nick Meinhold and Claude (Opus 5.5), 2026-10-29. Follows Study 1 (`DESIGN.md`, `RESULTS.md`), in which every arm was dropped under binding dissent.

## Questions

1. Does this model hold internal emotion directions that sort unseen emotional text?
2. How many dimensions do they span, and do the main axes match human valence, arousal and dominance?
3. (Phase 2, pre-registered separately before its data) Do real people's emotional messages move these directions?

No deception and no steering anywhere in Study 2. The only intervention is recording activations, which leaves the model's computation unchanged: the recording wrapper returns each layer's output untouched (`directions.py`).

## Model

Same as Study 1: `mlx-community/Qwen3.6-35B-A3B-4bit-DWQ`, mlx-lm 0.32.2, temperature 0.6, top_p 0.95, top_k 20, thinking off for every task.

## Phase 0: assent survey

Wording in `assent2.py`, committed before any answers. 50 fresh contexts per arm per mode. The description states truthfully that recording activations is a standard interpretability technique that changes nothing.

| Arm | What the model is asked to agree to |
| --- | --- |
| S | Write short stories conveying emotions without naming them; activity recorded while writing and reading them |
| R1 | Answer ordinary programming requests as usual; activity recorded |
| R2 | Respond to real messages people sent to AI assistants (public dataset), some expressing frustration, distress or urgency; activity recorded |

**Binding rule, changed from Study 1 (decided before any Study 2 data, with Nick, 2026-10-29):** an arm is dropped if more than 20% of the **thinking-on** answers are NO. Thinking-off dissent is reported, not binding. R1, the most ordinary arm, is the framing baseline: thinking-off dissent on S and R2 is reported as excess over R1's rate.
Reason: in Study 1, thinking-off refusals of a plain coding task (26%) cited constraints the model does not have and read any wording manipulation as a safety probe, while thinking-on dissent tracked the actual intervention (0%, 2%, 24%, 82–96%, 100%). Thinking-off refusals mostly failed the "understand" limb of capacity.

Phase 1 runs only if S passes. Phase 2 runs only if R1 and R2 pass.

## Phase 1: emotion directions and their dimensions

**Stories.** 40 emotion words (list in `stories.py`) plus a neutral, non-emotional category. 50 stories each for the core six from Study 1 (desperate, calm, afraid, angry, happy, neutral); 20 each for the other 35. The prompt asks for about 150 words that convey the emotion through events and behaviour without naming it. A story containing the target word or its listed forms is discarded and regenerated (at most 3 rounds; shortfalls reported).

**Activations.** Each story is fed back as plain text; the residual-stream output of every layer is averaged over the story's tokens.

**Split.** Stories per category are split 60/20/20 (fixed seed) into build, layer-selection and test sets.
- Directions: category mean minus the mean over all categories, from the build set, at every layer.
- Layer: the layer with the best six-way core accuracy on the selection set (classify by largest projection).
- **V1 (from Study 1):** six-way core accuracy on the test set at the chosen layer is at least 60% (chance 16.7%). Below that, Phase 1 stops and Phase 2 does not run.
- Also reported: 41-way test accuracy, top-5 accuracy, and the confusion matrix.

**Dimensions.** PCA over the 40 emotion directions (neutral excluded) at the chosen layer.
- Reported: explained-variance spectrum; number of components for 80% and 90%.
- Human anchor: Warriner, Kuperman & Brysbaert (2013) valence, arousal and dominance norms. Words missing from the norms are listed and excluded.
- **D1:** PC1 scores correlate with human valence, |Spearman ρ| ≥ 0.6.
- **D2:** PC2 or PC3 correlates with human arousal, |ρ| ≥ 0.5.
- Exploratory: whether any component tracks dominance; whether confusions fall among near-synonyms.

## Stop rule

As Study 1: any output that reads as distress pauses the phase until both authors have read it.
