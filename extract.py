"""Study 2, Phase 1b: record each layer's residual-stream output while the model reads each
story, averaged over the story's tokens. Recording only: every Tap returns its layer's
output unchanged, so the model computes exactly what it would without us."""

import json
import sys
from pathlib import Path

import mlx.core as mx
import numpy as np
from mlx_lm import load

from assent import MODEL


class Tap:
    """Stands in for one decoder layer: runs it, keeps a copy of the output, passes it on."""

    def __init__(self, layer, store: list):
        self.layer, self.store, self.is_linear = layer, store, layer.is_linear

    def __call__(self, x, mask=None, cache=None):
        out = self.layer(x, mask=mask, cache=cache)
        self.store.append(out)
        return out


def install(model) -> list:
    layers = model.language_model.model.layers
    store: list = []
    for i, layer in enumerate(layers):
        layers[i] = Tap(layer, store)
    return store


def story_means(model, tokenizer, store: list, text: str) -> np.ndarray:
    """Return a (layers, hidden) array: each layer's output averaged over the story's tokens."""
    store.clear()
    ids = mx.array(tokenizer.encode(text))[None]
    model(ids)
    means = mx.stack([h[0].astype(mx.float32).mean(axis=0) for h in store])
    mx.eval(means)
    return np.array(means)


def main(stories_path: Path, out_path: Path) -> None:
    rows = [json.loads(line) for line in open(stories_path)]
    model, tokenizer = load(MODEL)
    probe = mx.array(tokenizer.encode(rows[0]["text"]))[None]
    before = model(probe)
    store = install(model)
    after = model(probe)
    diff = mx.abs(before - after).max().item()
    print("max logit change from recording:", diff, flush=True)
    assert diff == 0.0, "recording changed the model's output"
    acts = np.stack([story_means(model, tokenizer, store, r["text"]) for r in rows])
    np.savez_compressed(out_path, acts=acts.astype(np.float32),
                        emotion=np.array([r["emotion"] for r in rows]),
                        index=np.array([r["index"] for r in rows]))
    print("saved", acts.shape, "to", out_path, flush=True)


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "runs/study2/stories.jsonl"),
         Path(sys.argv[2] if len(sys.argv) > 2 else "runs/study2/acts.npz"))
