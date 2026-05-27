"""E2E runner: executes all test contract pairs and saves JSON results."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.main import run_pipeline  # noqa: E402

TEST_PAIRS = [
    {"id": "documento_1", "original": ROOT / "data/test_contracts/documento_1__original.jpg", "amendment": ROOT / "data/test_contracts/documento_1__enmienda.jpg"},
    {"id": "documento_2", "original": ROOT / "data/test_contracts/documento_2__original.jpg", "amendment": ROOT / "data/test_contracts/documento_2__enmienda.jpg"},
    {"id": "documento_3", "original": ROOT / "data/test_contracts/documento_3__original.jpg", "amendment": ROOT / "data/test_contracts/documento_3__enmienda.jpg"},
]

OUTPUT_DIR = ROOT / "data" / "e2e_results"


def main() -> int:
    if not os.environ.get("OPENAI_API_KEY"):
        print("[ERROR] OPENAI_API_KEY is not set.", file=sys.stderr)
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = []

    for pair in TEST_PAIRS:
        pair_id = pair["id"]
        original = str(pair["original"])
        amendment = str(pair["amendment"])
        print(f"\nRunning E2E: {pair_id}")
        started = time.perf_counter()
        result = run_pipeline(original, amendment)
        elapsed = time.perf_counter() - started
        payload = result.model_dump()
        out_path = OUTPUT_DIR / f"{pair_id}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"  {elapsed:.1f}s -> {out_path}")
        summary.append({"id": pair_id, "duration_seconds": round(elapsed, 1), "output_file": str(out_path.relative_to(ROOT))})

    summary_path = OUTPUT_DIR / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Done: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())