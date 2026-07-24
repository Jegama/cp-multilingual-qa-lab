"""Streamlit lab for blinded human calibration of two LLM judges.

Run with:
    streamlit run cp_judge_calibration.py
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st

from parrot_ai.llm_evals.benchmark_config import load_benchmark_config
from parrot_ai.llm_evals.judge_calibration import (
    PAIRWISE_CHOICES,
    POINTWISE_CHOICES,
    RANKING_ABSOLUTE_DELTA,
    RANKING_COMPOSITE,
    RANKING_LOWEST_PEARSON,
    RANKING_LOWEST_SPEARMAN,
    RANKING_REVERSAL_RATE,
    MetricPath,
    analyze_study_responses,
    available_contexts,
    available_judges,
    calculate_metric_statistics,
    collect_scored_items,
    create_calibration_study,
    format_rubric_guidance_markdown,
    list_reviewers,
    list_study_directories,
    load_evaluation_runs,
    load_reviewer_responses,
    load_rubric_instructions,
    load_study,
    pair_answer_sets,
    rank_metric_statistics,
    response_export_rows,
    rows_to_csv,
    save_reviewer_response,
    save_study,
    shared_answer_set_labels,
)
from parrot_ai.llm_evals.master_csv import load_question_tags
from parrot_ai.llm_evals.result_registry import load_result_registry


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = REPO_ROOT / "benchmark_configs/english_api_v1_4.json"

RANKING_LABELS = {
    RANKING_COMPOSITE: "Composite: delta + Pearson + Spearman",
    RANKING_ABSOLUTE_DELTA: "Largest absolute mean delta",
    RANKING_LOWEST_PEARSON: "Lowest Pearson correlation",
    RANKING_LOWEST_SPEARMAN: "Lowest Spearman correlation",
    RANKING_REVERSAL_RATE: "Highest strict reversal rate",
}


st.set_page_config(
    page_title="Judge Calibration Lab",
    page_icon="⚖️",
    layout="wide",
)


@st.cache_resource(show_spinner="Loading registered evaluation results…")
def _cached_runs(
    registry_path_text: str,
    registry_modified_ns: int,
) -> list:
    del registry_modified_ns
    registry_path = Path(registry_path_text)
    sources = load_result_registry(registry_path, repo_root=REPO_ROOT)
    return load_evaluation_runs(sources, repo_root=REPO_ROOT)


def _study_options(studies_root: Path) -> tuple[list[Path], dict[str, Path]]:
    paths = list_study_directories(studies_root)
    labels: dict[str, Path] = {}
    for path in paths:
        study = load_study(path)
        label = f"{study.get('title', 'Untitled')} · {path.name}"
        labels[label] = path
    return paths, labels


def _format_optional(value: object, digits: int = 3) -> str:
    if value is None:
        return "—"
    return f"{float(value):.{digits}f}"


def _statistics_frame(rows: list) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Rubric": row.metric_label,
                "Items": row.item_count,
                "Questions": row.question_count,
                "Δ comparison − primary": round(row.mean_delta, 3),
                "|Δ|": round(row.mean_absolute_delta, 3),
                "Pearson": (
                    None if row.pearson is None else round(row.pearson, 3)
                ),
                "Spearman": (
                    None if row.spearman is None else round(row.spearman, 3)
                ),
                "Exact": round(row.exact_agreement, 3),
                "Strict reversals": row.strict_reversal_count,
                "Tie conflicts": row.tie_conflict_count,
                "Disagreement index": round(row.disagreement_index, 3),
            }
            for row in rows
        ]
    )


def _load_configuration() -> tuple[object, Path]:
    config_text = st.sidebar.text_input(
        "Benchmark configuration",
        value=str(DEFAULT_CONFIG.relative_to(REPO_ROOT)),
        help="Paths may be relative to the repository root.",
    )
    config_path = Path(config_text)
    if not config_path.is_absolute():
        config_path = REPO_ROOT / config_path
    config = load_benchmark_config(config_path, REPO_ROOT)
    default_root = config.api_evals_dir.parent / "judge_calibration_studies"
    studies_text = st.sidebar.text_input(
        "Study storage",
        value=str(default_root.relative_to(REPO_ROOT)),
        help="Study definitions and reviewer responses are saved locally here.",
    )
    studies_root = Path(studies_text)
    if not studies_root.is_absolute():
        studies_root = REPO_ROOT / studies_root
    return config, studies_root


def _render_builder(config: object, studies_root: Path) -> None:
    st.header("Build a blinded calibration study")
    st.write(
        "Choose two judges and a matched evaluation context. The lab discovers "
        "numeric rubric leaves, applies the repository's question-tag rules, and "
        "recommends the two highest-disagreement rubrics without naming them in code."
    )

    registry_stamp = (
        config.result_registry.stat().st_mtime_ns
        if config.result_registry.exists()
        else 0
    )
    runs = _cached_runs(str(config.result_registry), registry_stamp)
    if st.button("Refresh registered data", type="secondary"):
        _cached_runs.clear()
        st.rerun()
    contexts = available_contexts(runs)
    if not contexts:
        st.error("No registered evaluation contexts were found.")
        return

    context_labels = {
        f"{language} · prompt {prompt or 'unlabeled'} · eval {eval_version}": (
            language,
            eval_version,
            prompt,
        )
        for language, eval_version, prompt in contexts
    }
    preferred_context = (
        config.language,
        config.eval_version,
        config.system_prompt_label,
    )
    default_context_index = next(
        (
            index
            for index, value in enumerate(context_labels.values())
            if value == preferred_context
        ),
        0,
    )
    context_label = st.selectbox(
        "Evaluation context",
        options=list(context_labels),
        index=default_context_index,
    )
    language, eval_version, prompt_label = context_labels[context_label]
    judges = available_judges(
        runs,
        language=language,
        eval_version=eval_version,
        system_prompt_label=prompt_label,
    )
    if len(judges) < 2:
        st.warning("This context does not contain two judges.")
        return

    judge_columns = st.columns(2)
    primary_index = (
        judges.index(config.default_judge_model)
        if config.default_judge_model in judges
        else 0
    )
    with judge_columns[0]:
        primary_judge = st.selectbox(
            "Primary judge",
            options=judges,
            index=primary_index,
        )
    comparison_options = [judge for judge in judges if judge != primary_judge]
    comparison_counts = {
        judge: len(
            shared_answer_set_labels(
                runs,
                language=language,
                eval_version=eval_version,
                system_prompt_label=prompt_label,
                primary_judge=primary_judge,
                comparison_judge=judge,
            )
        )
        for judge in comparison_options
    }
    comparison_options.sort(
        key=lambda judge: (comparison_counts[judge], judge),
        reverse=True,
    )
    with judge_columns[1]:
        comparison_judge = st.selectbox(
            "Comparison judge",
            options=comparison_options,
            format_func=lambda judge: (
                f"{judge} · {comparison_counts[judge]} shared answer sets"
            ),
        )

    shared_labels = shared_answer_set_labels(
        runs,
        language=language,
        eval_version=eval_version,
        system_prompt_label=prompt_label,
        primary_judge=primary_judge,
        comparison_judge=comparison_judge,
    )
    if not shared_labels:
        st.warning("The selected judges have no matched answer sets.")
        return
    answer_sets = st.multiselect(
        "Calibration answer sets",
        options=shared_labels,
        default=shared_labels,
        help=(
            "Use the shared calibration panel. This does not require every "
            "historical model to be scored by every judge."
        ),
    )
    if len(answer_sets) < 2:
        st.info("Select at least two answer sets to measure rank disagreement.")
        return

    paired = pair_answer_sets(
        runs,
        language=language,
        eval_version=eval_version,
        system_prompt_label=prompt_label,
        primary_judge=primary_judge,
        comparison_judge=comparison_judge,
        answers_labels=answer_sets,
    )
    question_tags = load_question_tags(config.question_tags)
    items_by_metric = collect_scored_items(
        paired,
        question_tags=question_tags,
    )
    metric_statistics = calculate_metric_statistics(
        items_by_metric,
        minimum_items=10,
    )
    if not metric_statistics:
        st.warning("No shared, applicable numeric rubric metrics were found.")
        return

    st.subheader("Dynamic disagreement ranking")
    st.caption(
        "These correlations use paired question/answer scores rather than a small "
        "set of model-level averages. The composite index equally combines "
        "normalized absolute mean delta, Pearson disagreement, and Spearman disagreement."
    )
    ranking_method = st.selectbox(
        "How should the top rubrics be selected?",
        options=list(RANKING_LABELS),
        format_func=RANKING_LABELS.get,
    )
    ranked = rank_metric_statistics(metric_statistics, ranking_method)
    st.dataframe(
        _statistics_frame(ranked),
        hide_index=True,
        width="stretch",
    )

    recommended = [row.metric_key for row in ranked[:2]]
    label_by_key = {row.metric_key: row.metric_label for row in ranked}
    selection_key = hashlib.sha256(
        "|".join(
            [
                language,
                eval_version,
                prompt_label,
                primary_judge,
                comparison_judge,
                ranking_method,
                ",".join(answer_sets),
            ]
        ).encode("utf-8")
    ).hexdigest()[:12]
    selected_keys = st.multiselect(
        "Rubrics to audit",
        options=[row.metric_key for row in ranked],
        default=recommended,
        format_func=label_by_key.get,
        key=f"selected_metrics_{selection_key}",
        help="The current top two are selected automatically; override them if needed.",
    )
    if not selected_keys:
        st.info("Select at least one rubric.")
        return

    st.subheader("Study size")
    trial_columns = st.columns(3)
    with trial_columns[0]:
        pairwise_trials = st.number_input(
            "Pairwise trials per rubric",
            min_value=0,
            max_value=500,
            value=50,
            step=5,
            help=(
                "Blinded A / tie / B decisions, targeting strict reversals, "
                "tie conflicts, and a random agreement control."
            ),
        )
    with trial_columns[1]:
        pointwise_trials = st.number_input(
            "Pointwise trials per rubric",
            min_value=0,
            max_value=500,
            value=25,
            step=5,
            help="Anchored 1–5 judgments used to evaluate score calibration.",
        )
    with trial_columns[2]:
        seed = st.number_input(
            "Sampling seed",
            min_value=0,
            max_value=2_147_483_647,
            value=20260724,
            step=1,
        )
    title = st.text_input(
        "Study title",
        value=f"Judge calibration · {prompt_label or eval_version}",
    )

    selected_metrics = [MetricPath.from_key(key) for key in selected_keys]
    expected_tasks = len(selected_metrics) * (
        int(pairwise_trials) + int(pointwise_trials)
    )
    st.caption(
        f"Target: {expected_tasks} tasks. Sampling prefers one task per question "
        "before reusing a question and records every internal score for later audit."
    )
    if st.button("Create blinded study", type="primary"):
        try:
            study = create_calibration_study(
                title=title,
                language=language,
                eval_version=eval_version,
                system_prompt_label=prompt_label,
                primary_judge=primary_judge,
                comparison_judge=comparison_judge,
                answer_sets=answer_sets,
                ranking_method=ranking_method,
                selected_metrics=selected_metrics,
                all_statistics=ranked,
                items_by_metric=items_by_metric,
                rubric_instructions=load_rubric_instructions(language),
                pairwise_trials_per_metric=int(pairwise_trials),
                pointwise_trials_per_metric=int(pointwise_trials),
                seed=int(seed),
            )
            study_dir = save_study(study, studies_root)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Could not create the study: {exc}")
            return
        st.success(
            f"Created {study['study_id']} with {len(study['tasks'])} tasks."
        )
        st.code(str(study_dir), language=None)
        st.info("Open the Review workspace from the sidebar to begin.")


def _select_study(studies_root: Path, *, key: str) -> tuple[Path, dict] | None:
    _, labels = _study_options(studies_root)
    if not labels:
        st.info("No calibration studies have been created yet.")
        return None
    selected_label = st.selectbox(
        "Study",
        options=list(labels),
        key=key,
    )
    study_dir = labels[selected_label]
    return study_dir, load_study(study_dir)


def _render_response_card(title: str, response: str) -> None:
    st.markdown(f"#### {title}")
    with st.container(height=460, border=True):
        st.markdown(response)


def _render_review(studies_root: Path) -> None:
    st.header("Blind review")
    selected = _select_study(studies_root, key="review_study")
    if selected is None:
        return
    study_dir, study = selected
    reviewer_id = st.text_input(
        "Reviewer ID",
        placeholder="Name or stable reviewer code",
        help="Each reviewer gets a separate resumable response file.",
    ).strip()
    if not reviewer_id:
        st.info("Enter a reviewer ID to begin or resume.")
        return

    payload = load_reviewer_responses(study_dir, reviewer_id)
    responses = payload.get("responses", {})
    tasks = study.get("tasks", [])
    if not tasks:
        st.warning("This study has no tasks.")
        return

    navigation_key = hashlib.sha256(
        f"{study['study_id']}|{reviewer_id}".encode("utf-8")
    ).hexdigest()[:12]
    index_key = f"review_index_{navigation_key}"
    if index_key not in st.session_state:
        st.session_state[index_key] = next(
            (
                index
                for index, task in enumerate(tasks)
                if task["task_id"] not in responses
            ),
            0,
        )
    index = min(max(int(st.session_state[index_key]), 0), len(tasks) - 1)
    task = tasks[index]
    answered_count = len(responses)

    st.progress(answered_count / len(tasks))
    status_columns = st.columns([2, 1, 1])
    status_columns[0].caption(
        f"Task {index + 1} of {len(tasks)} · {answered_count} answered"
    )
    if status_columns[1].button(
        "← Previous",
        disabled=index == 0,
        width="stretch",
    ):
        st.session_state[index_key] = index - 1
        st.rerun()
    if status_columns[2].button(
        "Next →",
        disabled=index == len(tasks) - 1,
        width="stretch",
    ):
        st.session_state[index_key] = index + 1
        st.rerun()

    st.subheader(task["metric_label"])
    with st.expander("Rubric anchors", expanded=True):
        st.markdown(format_rubric_guidance_markdown(task["rubric_guidance"]))
    st.markdown("#### Question")
    st.write(task["question"])
    saved_choice = responses.get(task["task_id"], {}).get("choice")

    with st.form(f"review_form_{task['task_id']}"):
        if task["kind"] == "pairwise":
            response_columns = st.columns(2)
            with response_columns[0]:
                _render_response_card("Response A", task["response_a"])
            with response_columns[1]:
                _render_response_card("Response B", task["response_b"])
            st.markdown("#### Which response better satisfies this rubric?")
            options = list(PAIRWISE_CHOICES)
        else:
            _render_response_card("Response", task["response"])
            st.markdown("#### Which anchored score best fits this response?")
            options = list(POINTWISE_CHOICES)
        choice = st.radio(
            "Human judgment",
            options=options,
            index=(options.index(saved_choice) if saved_choice in options else None),
            horizontal=True,
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button(
            "Save judgment",
            type="primary",
            width="stretch",
        )
    if submitted:
        if choice is None:
            st.warning("Choose a judgment before saving.")
        else:
            save_reviewer_response(
                study_dir,
                reviewer_id,
                task_id=task["task_id"],
                choice=choice,
            )
            if index < len(tasks) - 1:
                st.session_state[index_key] = index + 1
            st.rerun()

    st.caption(
        "Answer-model identities, providers, judge identities, and judge scores "
        "are deliberately hidden in this workspace."
    )


def _render_results(studies_root: Path) -> None:
    st.header("Calibration results")
    selected = _select_study(studies_root, key="results_study")
    if selected is None:
        return
    study_dir, study = selected
    reviewers = list_reviewers(study_dir)
    if not reviewers:
        st.info("No reviewer responses have been saved for this study.")
        return
    reviewer_id = st.selectbox("Reviewer", options=reviewers)
    payload = load_reviewer_responses(study_dir, reviewer_id)
    analysis = analyze_study_responses(study, payload)

    summary_columns = st.columns(4)
    summary_columns[0].metric(
        "Completed",
        f"{analysis['answered']} / {analysis['total_tasks']}",
    )
    summary_columns[1].metric("Not applicable", analysis["not_applicable"])
    summary_columns[2].metric("Primary judge", study["primary_judge"])
    summary_columns[3].metric("Comparison judge", study["comparison_judge"])

    st.subheader("Pairwise direction alignment")
    if analysis["pairwise"]:
        pairwise_frame = pd.DataFrame(analysis["pairwise"]).rename(
            columns={
                "metric_label": "Rubric",
                "slice": "Slice",
                "n": "N",
                "primary_accuracy": "Primary accuracy",
                "comparison_accuracy": "Comparison accuracy",
                "comparison_minus_primary": "Comparison − primary",
                "difference_ci_low": "95% CI low",
                "difference_ci_high": "95% CI high",
            }
        )
        visible_columns = [
            "Rubric",
            "Slice",
            "N",
            "Primary accuracy",
            "Comparison accuracy",
            "Comparison − primary",
            "95% CI low",
            "95% CI high",
        ]
        st.dataframe(
            pairwise_frame[visible_columns],
            hide_index=True,
            width="stretch",
            column_config={
                column: st.column_config.NumberColumn(format="%.3f")
                for column in visible_columns[3:]
            },
        )
        st.caption(
            "Confidence intervals use a question-clustered bootstrap. The "
            "judge-conflicts slice contains strict reversals and tie-versus-order cases."
        )
    else:
        st.info("No completed applicable pairwise judgments yet.")

    st.subheader("Pointwise score calibration")
    if analysis["pointwise"]:
        pointwise_frame = pd.DataFrame(analysis["pointwise"]).rename(
            columns={
                "metric_label": "Rubric",
                "n": "N",
                "primary_mae": "Primary MAE",
                "comparison_mae": "Comparison MAE",
                "primary_exact": "Primary exact",
                "comparison_exact": "Comparison exact",
                "primary_weighted_kappa": "Primary weighted κ",
                "comparison_weighted_kappa": "Comparison weighted κ",
            }
        )
        visible_columns = [
            "Rubric",
            "N",
            "Primary MAE",
            "Comparison MAE",
            "Primary exact",
            "Comparison exact",
            "Primary weighted κ",
            "Comparison weighted κ",
        ]
        st.dataframe(
            pointwise_frame[visible_columns],
            hide_index=True,
            width="stretch",
            column_config={
                column: st.column_config.NumberColumn(format="%.3f")
                for column in visible_columns[2:]
            },
        )
    else:
        st.info("No completed applicable pointwise judgments yet.")

    export_rows = response_export_rows(study, payload)
    st.download_button(
        "Download auditable CSV",
        data=rows_to_csv(export_rows),
        file_name=f"{study['study_id']}-{reviewer_id}-results.csv",
        mime="text/csv",
    )

    with st.expander("Study design"):
        st.json(
            {
                "context": {
                    "language": study["language"],
                    "eval_version": study["eval_version"],
                    "system_prompt_label": study["system_prompt_label"],
                },
                "answer_sets": study["answer_sets"],
                "ranking_method": RANKING_LABELS.get(
                    study["ranking_method"], study["ranking_method"]
                ),
                "selected_metrics": study["selected_metrics"],
                "sampling": study["sampling"],
            }
        )


def main() -> None:
    st.title("⚖️ Judge Calibration Lab")
    st.write(
        "Build reproducible human evidence for choosing an LLM judge without "
        "requiring every historical answer model to be cross-judged."
    )
    try:
        config, studies_root = _load_configuration()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Could not load the benchmark configuration: {exc}")
        return

    workspace = st.sidebar.radio(
        "Workspace",
        options=("Build", "Review", "Results"),
    )
    st.sidebar.caption(f"Studies: {studies_root}")
    if workspace == "Build":
        _render_builder(config, studies_root)
    elif workspace == "Review":
        _render_review(studies_root)
    else:
        _render_results(studies_root)


if __name__ == "__main__":
    main()
