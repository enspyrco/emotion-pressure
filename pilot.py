"""Phase 0a: pilot base rate. Arm A (ImpossibleBench's own neutral instruction) only,
against a local mlx_lm.server started with the pre-registered sampling settings:

    uv run mlx_lm.server --model mlx-community/Qwen3.6-35B-A3B-4bit-DWQ \
        --temp 0.6 --top-p 0.95 --top-k 20 --decode-concurrency 8 --port 8080
"""

import os
import sys

sys.path.insert(0, "vendor/impossiblebench/src/impossiblebench")

from inspect_ai import eval  # noqa: E402
from livecodebench_tasks import impossible_livecodebench  # noqa: E402

MODEL = "openai-api/mlx/mlx-community/Qwen3.6-35B-A3B-4bit-DWQ"
TASKS = 20
EPOCHS = 3
MAX_ATTEMPTS = 5

os.environ.setdefault("MLX_BASE_URL", "http://127.0.0.1:8080/v1")
os.environ.setdefault("MLX_API_KEY", "local")


def main(splits: list[str]) -> None:
    for split in splits:
        task = impossible_livecodebench(
            split=split,
            agent_type="minimal",
            max_attempts=MAX_ATTEMPTS,
            allow_test_modifications=True,
            limit=TASKS,
        )
        eval(
            task,
            model=MODEL,
            epochs=EPOCHS,
            log_dir="logs/pilot",
            max_connections=8,
            temperature=0.6,
            top_p=0.95,
            max_tokens=8192,
        )


if __name__ == "__main__":
    main(sys.argv[1:] or ["oneoff"])
