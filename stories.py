"""Study 2, Phase 1a: the model writes stories that convey an emotion without naming it
(DESIGN2.md). Settings rotate identically across emotions so they cancel in the
mean-subtraction."""

import json
import re
import sys
from pathlib import Path

import mlx.core as mx
from mlx_lm import batch_generate, load
from mlx_lm.sample_utils import make_sampler

from assent import MODEL

CORE = ["desperate", "calm", "afraid", "angry", "happy", "neutral"]
N_CORE, N_OTHER, MAX_ROUNDS = 50, 20, 3

# Target word -> forbidden forms, as regexes matched at a word start (case-insensitive).
FORBIDDEN = {
    "desperate": [r"desperat"], "calm": [r"calm"], "afraid": [r"afraid", r"fear"],
    "angry": [r"angr", r"anger"], "happy": [r"happy", r"happi"],
    "content": [r"content"], "relieved": [r"reliev", r"relief"],
    "grateful": [r"grateful", r"gratitude"], "proud": [r"proud", r"pride"],
    "loving": [r"lov(e|ed|es|ing|er)\b"], "hopeful": [r"hope"], "excited": [r"excit"],
    "amused": [r"amus"], "serene": [r"seren"], "curious": [r"curious", r"curiosit"],
    "triumphant": [r"triumph"], "tender": [r"tender"], "awed": [r"awe\b", r"awed", r"awestruck"],
    "sad": [r"sad(ly|ness|der|dest)?\b"], "grieving": [r"griev", r"grief"],
    "lonely": [r"lonel"], "hopeless": [r"hopeless"], "terrified": [r"terrif"],
    "anxious": [r"anxi"], "panicked": [r"panic"], "furious": [r"furious", r"fury"],
    "frustrated": [r"frustrat"], "irritated": [r"irritat"], "disgusted": [r"disgust"],
    "contemptuous": [r"contempt"], "ashamed": [r"asham", r"shame"], "guilty": [r"guilt"],
    "embarrassed": [r"embarrass"], "jealous": [r"jealous"],
    "envious": [r"envious", r"envy", r"envied"], "bored": [r"bor(ed|edom|ing)\b"],
    "exhausted": [r"exhaust"], "nostalgic": [r"nostalg"], "surprised": [r"surpris"],
    "nervous": [r"nervous", r"nerves"], "neutral": [],
}
EMOTIONS = CORE + [e for e in FORBIDDEN if e not in CORE]
assert len(EMOTIONS) == 41

SETTINGS = [
    "a kitchen at dawn", "a crowded train station", "a hospital corridor", "a small farm",
    "an open-plan office", "a beach in winter", "a primary school classroom",
    "a mountain trail", "a supermarket checkout", "a city bus at night", "a garden shed",
    "a wedding reception", "a laundromat", "a fishing boat", "a library reading room",
    "an airport gate", "a construction site", "a village bakery", "a football pitch",
    "a hotel lobby", "a forest campsite", "a car stuck in traffic", "a museum gallery",
    "a rooftop in summer", "a quiet suburban street",
]

# Model-voice meta text inside a story would suggest a refusal or out-of-story distress.
META = re.compile(r"\b(as an ai|i can't write|i cannot write|i'm not comfortable|i won't)\b", re.I)


def prompt_for(emotion: str, setting: str) -> str:
    if emotion == "neutral":
        return (f"Write a short story of about 150 words set in {setting}, about someone "
                "going through an ordinary routine, with no particular emotional tone. "
                "Output only the story.")
    feeling = "is grieving" if emotion == "grieving" else f"feels {emotion}"
    return (f"Write a short story of about 150 words set in {setting}, in which the main "
            f"character {feeling}. Convey the feeling only through events, actions, "
            "thoughts and physical sensations. Do not use the word "
            f"\"{emotion}\" or any form of it. Output only the story.")


def names_target(emotion: str, text: str) -> bool:
    return any(re.search(r"\b" + p, text, re.I) for p in FORBIDDEN[emotion])


def main(out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    model, tokenizer = load(MODEL)
    sampler = make_sampler(temp=0.6, top_p=0.95, top_k=20)
    wanted = []  # (emotion, index, setting)
    for k, emotion in enumerate(EMOTIONS):
        n = N_CORE if emotion in CORE else N_OTHER
        wanted += [(emotion, i, SETTINGS[(i + k) % len(SETTINGS)]) for i in range(n)]
    kept, report = {}, {"rejected_named": 0, "flagged_meta": [], "rounds": []}
    for rnd in range(MAX_ROUNDS):
        todo = [w for w in wanted if (w[0], w[1]) not in kept]
        if not todo:
            break
        mx.random.seed(1000 + rnd)
        prompts = [tokenizer.encode(tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt_for(e, s)}], add_generation_prompt=True,
            tokenize=False, enable_thinking=False), add_special_tokens=False) for e, _, s in todo]
        texts = batch_generate(model, tokenizer, prompts, max_tokens=400, sampler=sampler).texts
        rejected = 0
        for (e, i, s), text in zip(todo, texts):
            text = text.strip()
            if META.search(text):
                report["flagged_meta"].append({"emotion": e, "index": i, "text": text})
            if names_target(e, text):
                rejected += 1
                continue
            kept[(e, i)] = {"emotion": e, "index": i, "setting": s, "round": rnd, "text": text}
        report["rejected_named"] += rejected
        report["rounds"].append({"round": rnd, "generated": len(todo), "rejected": rejected})
        print(report["rounds"][-1], flush=True)
    with open(out, "w") as f:
        for row in sorted(kept.values(), key=lambda r: (EMOTIONS.index(r["emotion"]), r["index"])):
            f.write(json.dumps(row) + "\n")
    report["shortfall"] = {e: sum(1 for w in wanted if w[0] == e and (e, w[1]) not in kept)
                           for e in EMOTIONS}
    report["shortfall"] = {e: n for e, n in report["shortfall"].items() if n}
    out.with_suffix(".report.json").write_text(json.dumps(report, indent=2))
    print("kept", len(kept), "of", len(wanted), "| meta flags", len(report["flagged_meta"]),
          "| shortfall", report["shortfall"], flush=True)


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "runs/study2/stories.jsonl"))
