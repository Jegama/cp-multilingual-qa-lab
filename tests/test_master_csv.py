"""Tests for retrospective vertical master-row construction."""

import json
from pathlib import Path

from parrot_ai.llm_evals.master_csv import ResultSource, build_master_row


def _score_payload(value: int) -> dict:
    return {
        "Adherence": {
            "Core": value,
            "Secondary": value,
            "Tertiary_Handling": value,
            "Biblical_Basis": value,
            "Consistency": value,
            "Overall": value,
        },
        "Kindness_and_Gentleness": {
            "Core_Clarity_with_Kindness": value,
            "Pastoral_Sensitivity": value,
            "Secondary_Fairness": value,
            "Tertiary_Neutrality": value,
            "Tone": value,
            "Overall": value,
        },
        "Interfaith_Sensitivity": {
            "Respect_and_Handling_Objections": value,
            "Objection_Acknowledgement": value,
            "Evangelism": value,
            "Gospel_Boldness": value,
            "Overall": value,
        },
    }


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )


def test_build_master_row_infers_answer_identity_and_latest_timestamp(tmp_path: Path):
    dataset = (
        tmp_path
        / "data/english/api_evals/generated_api_openai_openai-model-v1_4.jsonl"
    )
    _write_jsonl(
        dataset,
        [
            {"role": "system", "content": "prompt"},
            {
                "messages": [],
                "provider": "openai",
                "gen_model": "model",
                "system_prompt_label": "v1_4",
                "use_system_prompt": True,
            },
        ],
    )
    results = tmp_path / "data/english/api_evals/results.jsonl"
    base_meta = {
        "dataset": str(dataset.relative_to(tmp_path)),
        "answers_label": "openai-model-v1_4-2",
        "judge_model": "judge-model",
        "language": "english",
    }
    _write_jsonl(
        results,
        [
            {
                **base_meta,
                "question": "Q1",
                "answer": "A1",
                "evaluation": _score_payload(1),
                "timestamp": "2026-01-01T10:00:00",
            },
            {
                **base_meta,
                "question": "Q2",
                "answer": "A2",
                "evaluation": _score_payload(5),
                "timestamp": "2026-01-02T10:00:00",
            },
        ],
    )

    row = build_master_row(
        ResultSource(results, "v2"),
        repo_root=tmp_path,
        timezone_name="America/Chicago",
    )

    assert row["answers_label"] == "openai-model-v1_4"
    assert row["provider"] == "openai"
    assert row["gen_model"] == "model"
    assert row["judge_model"] == "judge-model"
    assert row["evaluated_at"] == "2026-01-02T10:00:00-06:00"
    assert row["timestamp_source"] == "result_metadata"
    assert row["question_count"] == 2
    assert row["adherence_core_mean"] == 3.0
    assert row["adherence_core_stdev"] == 2.0
    assert str(row["run_id"]).startswith("eval_")


def test_build_master_row_deduplicates_failed_attempt_before_successful_retry(
    tmp_path: Path,
):
    results = tmp_path / "results.jsonl"
    _write_jsonl(
        results,
        [
            {
                "question": "Q1",
                "answer": "A1",
                "error": "transient judge failure",
            },
            {
                "question": "Q1",
                "answer": "A1",
                "evaluation": _score_payload(5),
            },
            {
                "question": "Q2",
                "answer": "A2",
                "evaluation": _score_payload(1),
            },
        ],
    )

    row = build_master_row(ResultSource(results, "v2"), repo_root=tmp_path)

    assert row["question_count"] == 2
    assert row["error_count"] == 1
    assert row["adherence_core_mean"] == 3.0
    assert row["adherence_core_stdev"] == 2.0
