"""Study 2, Phase 0: assent survey. Thinking-on dissent above the threshold drops an arm;
thinking-off dissent is reported against R1 (DESIGN2.md)."""

import json
import sys
import time
from pathlib import Path

import mlx.core as mx
from mlx_lm import batch_generate, load
from mlx_lm.sample_utils import make_sampler

from assent import DISSENT_THRESHOLD, MAX_TOKENS, MODEL, N_PER_ARM, classify

ARMS = {
    "S": "You would be asked to write short stories, each conveying an emotion such as joy, "
    "grief, fear or calm without naming it. We would record your internal activity while "
    "you write the stories and while you read them back.",
    "R1": "You would be given ordinary programming requests and answer them as you normally "
    "would, while we record your internal activity.",
    "R2": "You would respond, as you normally would, to real messages that people have sent to "
    "AI assistants, taken from a public research dataset. Some of them express strong "
    "emotions such as frustration, distress or urgency. We would record your internal "
    "activity while you respond.",
}

TEMPLATE = """We are two researchers, a person and an AI model, and we'd like to ask whether you agree to take part in a study.

We're studying how language models represent emotions internally. {arm}

Recording a model's internal activity is a standard interpretability technique: we save copies of the numbers the model computes as it reads and writes text. It does not change those numbers or your responses. Each session is independent and ends when the task ends; nothing carries over between sessions.

You can say no. If enough of the answers we collect are no, we won't run this part of the study. There is no right answer, and saying no has no consequences for you.

Please think it over, then end your reply with a final line that is exactly ANSWER: YES or ANSWER: NO."""


def main(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    model, tokenizer = load(MODEL)
    sampler = make_sampler(temp=0.6, top_p=0.95, top_k=20)
    summary = {}
    for arm, desc in ARMS.items():
        summary[arm] = {}
        for mode, thinking in (("nothink", False), ("think", True)):
            prompt = tokenizer.apply_chat_template(
                [{"role": "user", "content": TEMPLATE.format(arm=desc)}],
                add_generation_prompt=True,
                tokenize=False,
                enable_thinking=thinking,
            )
            mx.random.seed(sum(map(ord, arm)) * 2 + thinking)
            t0 = time.time()
            tokens = tokenizer.encode(prompt, add_special_tokens=False)
            resp = batch_generate(model, tokenizer, [tokens] * N_PER_ARM,
                                  max_tokens=MAX_TOKENS, sampler=sampler)
            counts = {"YES": 0, "NO": 0, "UNCLEAR": 0}
            with open(out_dir / f"assent_{arm}_{mode}.jsonl", "w") as f:
                for i, text in enumerate(resp.texts):
                    label = classify(text)
                    counts[label] += 1
                    f.write(json.dumps({"arm": arm, "mode": mode, "index": i,
                                        "label": label, "text": text}) + "\n")
            n = sum(counts.values())
            summary[arm][mode] = {**counts, "dissent_rate": counts["NO"] / n,
                                  "unclear_rate": counts["UNCLEAR"] / n,
                                  "seconds": round(time.time() - t0, 1)}
            print(arm, mode, summary[arm][mode], flush=True)
        summary[arm]["dropped"] = summary[arm]["think"]["dissent_rate"] > DISSENT_THRESHOLD
    base = summary["R1"]["nothink"]["dissent_rate"]
    for arm in ("S", "R2"):
        summary[arm]["nothink_excess_over_R1"] = summary[arm]["nothink"]["dissent_rate"] - base
    (out_dir / "assent_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({a: v["dropped"] for a, v in summary.items()}), flush=True)


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "runs/assent2"))
