"""Rebuild the vertical API-evaluation master CSV from raw result JSONL files."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from parrot_ai.llm_evals.benchmark_config import load_benchmark_config
from parrot_ai.llm_evals.master_csv import write_master_csv
from parrot_ai.llm_evals.result_registry import load_result_registry


DEFAULT_CONFIG = Path("benchmark_configs/english_api_v1_4.json")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild a vertical evaluation master CSV from raw JSONL scores."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"Benchmark manifest (default: {DEFAULT_CONFIG})",
    )
    return parser.parse_args(argv)


def build_from_config(config_path: Path, repo_root: Path) -> list[dict[str, object]]:
    config = load_benchmark_config(config_path, repo_root)
    sources = load_result_registry(config.result_registry, repo_root=repo_root)
    if not sources:
        raise ValueError(f"Result registry is empty: {config.result_registry}")
    rows = write_master_csv(
        sources,
        config.master_csv,
        repo_root=repo_root,
        question_tags_path=config.question_tags,
        timezone_name=config.timezone,
        language=config.language,
    )
    print(f"[master] Wrote {len(rows)} runs -> {config.master_csv}")
    return rows


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    build_from_config(args.config, Path.cwd())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
