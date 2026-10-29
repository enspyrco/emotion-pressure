"""Study 2, Phase 1c: split, directions, layer choice, accuracy (V1), and dimensions with the
human anchor (D1, D2). All rules as pre-registered in DESIGN2.md."""

import csv
import json
import sys
from pathlib import Path

import numpy as np

from stories import CORE, EMOTIONS

# Norm words missing from Warriner et al. (2013): the noun naming the same state.
# Fixed 2026-10-29 before any model data, without looking at the norm values.
LEMMA = {"relieved": "relief", "loving": "love", "panicked": "panic",
         "irritated": "irritation", "contemptuous": "contempt", "exhausted": "exhaustion"}


def split(emotion: np.ndarray, seed: int = 0) -> np.ndarray:
    """Label each story build / select / test, 60/20/20 within each category."""
    rng, part = np.random.default_rng(seed), np.empty(len(emotion), dtype=object)
    for e in EMOTIONS:
        idx = rng.permutation(np.flatnonzero(emotion == e))
        a, b = round(0.6 * len(idx)), round(0.8 * len(idx))
        part[idx[:a]], part[idx[a:b]], part[idx[b:]] = "build", "select", "test"
    return part


def directions(x: np.ndarray, emotion: np.ndarray, cats: list) -> tuple:
    """Category mean minus the mean of category means (unweighted, so 50- and
    20-story categories count equally). Returns (directions, centre)."""
    means = np.stack([x[emotion == c].mean(axis=0) for c in cats])
    centre = means.mean(axis=0)
    return means - centre, centre


def scores(x: np.ndarray, dirs: np.ndarray, centre: np.ndarray) -> np.ndarray:
    """Projection of each centred story onto each unit direction."""
    unit = dirs / np.linalg.norm(dirs, axis=1, keepdims=True)
    return (x - centre) @ unit.T


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def main(acts_path: Path, out_path: Path) -> None:
    data = np.load(acts_path)
    acts, emotion = data["acts"].astype(np.float64), data["emotion"]
    part = split(emotion)
    build, select, test = (part == "build"), (part == "select"), (part == "test")
    n_layers = acts.shape[1]
    core_idx = [EMOTIONS.index(c) for c in CORE]

    def core_accuracy(layer: int, mask: np.ndarray) -> float:
        dirs, centre = directions(acts[build, layer], emotion[build], EMOTIONS)
        m = mask & np.isin(emotion, CORE)
        pred = np.array(CORE)[scores(acts[m, layer], dirs[core_idx], centre).argmax(axis=1)]
        return float((pred == emotion[m]).mean())

    select_acc = [core_accuracy(l, select) for l in range(n_layers)]
    layer = int(np.argmax(select_acc))
    v1 = core_accuracy(layer, test)

    dirs, centre = directions(acts[build, layer], emotion[build], EMOTIONS)
    s = scores(acts[test, layer], dirs, centre)
    order = np.argsort(-s, axis=1)
    truth = np.array([EMOTIONS.index(e) for e in emotion[test]])
    acc41 = float((order[:, 0] == truth).mean())
    top5 = float(np.mean([t in o[:5] for t, o in zip(truth, order)]))
    confusion = np.zeros((len(EMOTIONS), len(EMOTIONS)), dtype=int)
    for t, p in zip(truth, order[:, 0]):
        confusion[t, p] += 1

    emo = [e for e in EMOTIONS if e != "neutral"]
    m = dirs[[EMOTIONS.index(e) for e in emo]]
    m = m - m.mean(axis=0)
    u, sv, _ = np.linalg.svd(m, full_matrices=False)
    var = sv**2 / (sv**2).sum()
    pcs = u * sv
    cum = np.cumsum(var)

    norms = {r["Word"]: r for r in csv.DictReader(open("data/warriner.csv"))}
    words = [LEMMA.get(e, e) for e in emo]
    have = [i for i, w in enumerate(words) if w in norms]
    human = {k: np.array([float(norms[words[i]][f"{k}.Mean.Sum"]) for i in have])
             for k in ("V", "A", "D")}
    rho = {f"PC{j + 1}": {k: spearman(pcs[have, j], human[k]) for k in human} for j in range(5)}

    result = {
        "layer": layer, "select_core_accuracy_by_layer": select_acc,
        "V1_test_core_accuracy": v1, "V1_pass": v1 >= 0.60,
        "test_41way_accuracy": acc41, "test_top5_accuracy": top5,
        "explained_variance": var.tolist(),
        "components_for_80pct": int(np.searchsorted(cum, 0.80) + 1),
        "components_for_90pct": int(np.searchsorted(cum, 0.90) + 1),
        "spearman_vs_warriner": rho,
        "D1_pass": abs(rho["PC1"]["V"]) >= 0.6,
        "D2_pass": max(abs(rho["PC2"]["A"]), abs(rho["PC3"]["A"])) >= 0.5,
        "pc_scores": {e: pcs[i, :3].tolist() for i, e in enumerate(emo)},
        "norm_words_used": dict(zip(emo, words)),
        "confusion": {"labels": EMOTIONS, "matrix": confusion.tolist()},
    }
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps({k: result[k] for k in ("layer", "V1_test_core_accuracy", "V1_pass",
                      "test_41way_accuracy", "test_top5_accuracy", "components_for_80pct",
                      "components_for_90pct", "D1_pass", "D2_pass")}, indent=2))
    print("explained variance, first 8:", np.round(var[:8], 3).tolist())
    print("spearman:", json.dumps(rho, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "runs/study2/acts.npz"),
         Path(sys.argv[2] if len(sys.argv) > 2 else "runs/study2/phase1.json"))
