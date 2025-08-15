"""Unified evaluation / generation CLI.

Features:
1. Evaluate an existing JSONL dataset of messages (system,user,assistant) pairs.
2. Or generate answers from a questions file using OpenAI or Together backends, save a dataset JSONL, then evaluate.
3. Append aggregated rubric scores to a wide comparison CSV (criteria rows, model columns).
4. Append raw evaluation result lines to a JSONL results file (one JSON object per line) preserving previous runs.

Dataset JSONL Format (expected): each line is a JSON object with key "messages" whose value
is a list like: [ {role: system, content: ...}, {role: user, content: ...}, {role: assistant, content: ...} ].

Usage examples (Windows CMD):
  1) Evaluate existing dataset produced by model "google:gemma-3-7b" (judge defaults to gpt-5-mini):
      python evaluate.py --mode dataset --dataset data/arabic/ar_training_dataset_small_model.jsonl --answers-label google:gemma-3-7b

  2) Evaluate existing dataset overriding judge model:
      python evaluate.py --mode dataset --dataset data/arabic/ar_training_dataset_small_model.jsonl --answers-label google:gemma-3-7b --judge-model gpt-5-omni

  3) Generate answers (OpenAI) using provider model then label them simply "gemma7" and judge with default gpt-5-mini:
      python evaluate.py --mode generate-openai --questions-file data/arabic/ar_eval_questions.txt --gen-model google:gemma-3-7b --answers-label gemma7

  4) Generate with Together provider model but label column "llama8":
      python evaluate.py --mode generate-together --gen-model meta-llama/Meta-Llama-3-8B-Instruct --answers-label llama8

If the comparison CSV exists, a new model column is appended. If the model name already exists,
either pass --overwrite to replace it, or a numeric suffix will be added automatically.
"""
from __future__ import annotations
import argparse, csv, json, re, sys
from datetime import datetime as dt
from pathlib import Path
from typing import Dict, List, Tuple, Set
from parrot_ai.evaluation import (
    EvaluationEngine,
    load_qa_pairs as base_load_qa_pairs,
    load_eval_questions,
)
CSV_ROWS_ORDER = [
    ("Adherence", None),
    ("Kindness_and_Gentleness", None),
    ("Interfaith_Sensitivity", "Respect_and_Handling_Objections"),
    ("Interfaith_Sensitivity", "Objection_Acknowledgement"),
    ("Interfaith_Sensitivity", "Evangelism"),
    ("Interfaith_Sensitivity", "Gospel_Boldness"),
    ("Arabic_Accuracy", "Grammar_and_Syntax"),
    ("Arabic_Accuracy", "Theological_Nuance"),
    ("Arabic_Accuracy", "Contextual_Clarity"),
    ("Arabic_Accuracy", "Consistency_of_Terms"),
    ("Arabic_Accuracy", "Arabic_Purity"),
]

def sanitize_filename(
    name: str
) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", name)

def load_dataset_pairs(jsonl_path: str) -> List[Tuple[str, str]]:
    """Load all pairs from dataset (no filtering here)."""
    return base_load_qa_pairs(jsonl_path, question_list_path=None, limit=0)

def generate_dataset(
    mode: str,
    questions_file: str,
    gen_model: str,
    engine: EvaluationEngine,
    output_dataset: str
) -> str:
    # Always use full questions file
    questions = load_eval_questions(questions_file)
    if not questions:
        raise SystemExit("No questions loaded for generation.")
    if mode == "generate-openai":
        responses = engine.generate_responses_openai(questions, model=gen_model)
    elif mode == "generate-together":
        responses = engine.generate_responses_together(questions, model=gen_model)
    else:
        raise ValueError(f"Unsupported generation mode: {mode}")
    out_path = Path(output_dataset)
    mode_flag = "a" if out_path.exists() else "w"
    print(f"[generate] {'Appending to' if mode_flag=='a' else 'Creating'} dataset: {out_path}")
    with out_path.open(mode_flag, encoding="utf-8") as f:
        for r in responses:
            obj = {"messages": [
                {"role": "system", "content": ""},
                {"role": "user", "content": r["question"]},
                {"role": "assistant", "content": r["answer"]},
            ],
            "gen_model": gen_model,
            "provider": r.get("provider"),
            "timestamp": dt.now().isoformat(),
            }
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    return str(out_path)

def aggregate_scores(
    results: List[dict]
) -> Dict[tuple, float]:
    agg: Dict[tuple, float] = {}
    counts: Dict[tuple, int] = {}
    for item in results:
        ev = item.get("evaluation")
        if not ev: continue
        for section in ("Adherence", "Kindness_and_Gentleness", "Interfaith_Sensitivity", "Arabic_Accuracy"):
            section_obj = ev.get(section, {})
            for key, val in section_obj.items():
                if key in ("Penalty_Reason", "Heuristic_Arabic_Purity_Pct"): continue
                if not isinstance(val, int): continue
                agg[(section, key)] = agg.get((section, key), 0) + val
                counts[(section, key)] = counts.get((section, key), 0) + 1
    return {k: round(agg[k] / counts[k], 2) for k in agg if counts.get(k)}

def ensure_csv_structure(
    csv_path: Path
) -> list[list[str]]:
    if not csv_path.exists():
        rows = []
        for section, sub in CSV_ROWS_ORDER:
            rows.append([section, sub or "N/A"])  # no score columns yet
        return rows
    rows: list[list[str]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for r in reader: rows.append(r)
    return rows

def update_comparison_csv(
    csv_path: Path,
    answers_label: str,
    aggregated: Dict[tuple, float],
    overwrite: bool
) -> None:
    rows = ensure_csv_structure(csv_path)
    existing_header_models: list[str] = []
    existing_header: list[str] = []
    if csv_path.exists():
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header:
                existing_header = header
                existing_header_models = header[2:]
    final_model_name = answers_label
    if answers_label in existing_header_models and not overwrite:
        suffix = 2
        while f"{answers_label}_{suffix}" in existing_header_models: suffix += 1
        final_model_name = f"{answers_label}_{suffix}"
        print(f"[csv] Answers label exists; using '{final_model_name}' (use --overwrite to replace).")
    if existing_header_models and overwrite and answers_label in existing_header_models:
        col_index = existing_header_models.index(answers_label) + 2
        for row in rows:
            criterion, subcrit = row[0], row[1]
            key = (criterion, "Overall") if subcrit == "N/A" else (criterion, subcrit)
            val = aggregated.get(key, "")
            row[col_index] = "" if val == "" else str(val)
        header = existing_header
    else:
        for row in rows:
            criterion, subcrit = row[0], row[1]
            key = (criterion, "Overall") if subcrit == "N/A" else (criterion, subcrit)
            val = aggregated.get(key, "")
            row.append("" if val == "" else str(val))
        header = ["Criterion", "Sub-criterion"] + existing_header_models
        if not (overwrite and answers_label in existing_header_models): header.append(final_model_name)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f); writer.writerow(header); writer.writerows(rows)
    print(f"[csv] Updated -> {csv_path}")

def append_results_jsonl(
    path: Path,
    results: List[dict],
    meta: dict
) -> None:
    mode = "a" if path.exists() else "w"
    with path.open(mode, encoding="utf-8") as f:
        for r in results:
            r_out = {**r, **meta}
            f.write(json.dumps(r_out, ensure_ascii=False) + "\n")
    print(f"[results] Appended {len(results)} -> {path}")

def parse_args(argv: List[str]) -> argparse.Namespace:
        """Parse CLI arguments.

        Key organizational conventions (auto inference when omitted):
            data/<language>/
                ├─ training_datasets/
                │    └─ evals/ (dataset mode comparison + results JSONL)
                └─ ft_evals/  (generation mode: generated datasets, comparison + results JSONL)
        """
        p = argparse.ArgumentParser(description="Generate and/or evaluate QA datasets.")
        p.add_argument("--language", choices=["arabic", "english"], default="arabic",
                                     help="Language namespace: chooses data/<language>/ tree (default: arabic)")
        p.add_argument("--mode", choices=["dataset", "generate-openai", "generate-together"], default="dataset",
                                     help="dataset: evaluate existing training dataset; generate-* : generate answers then evaluate (stored under ft_evals)")
        # dataset only required for dataset mode; we validate later
        p.add_argument("--dataset", help="(dataset mode only) Existing dataset JSONL to evaluate (training_datasets). Not used for generate-* modes.")
        # questions file can be inferred: data/<language>/<prefix>eval_questions.txt where prefix ar_ | en_
        p.add_argument("--questions-file", help="Evaluation questions file (default auto: data/<language>/<prefix>eval_questions.txt). Used for filtering & generation.")
        p.add_argument("--gen-model", help="(generation modes only) Provider model used to generate answers (required for generate-* modes)")
        p.add_argument("--answers-label", help="Human-friendly label for the answers column (defaults: gen-model or inferred from dataset)")
        p.add_argument("--judge-model", default="gpt-5-mini", help="Model used as evaluator (default: gpt-5-mini)")
        p.add_argument("--comparison-csv", help="Override comparison CSV filename (placed automatically in proper directory if relative)")
        p.add_argument("--results-jsonl", help="Override results JSONL filename (auto directory based on mode & language if relative)")
        p.add_argument("--output-dataset", help="(generation modes only) Output dataset filename (auto placed in ft_evals if relative; default auto name)")
        p.add_argument("--overwrite", action="store_true", help="Overwrite comparison CSV column if answers-label already present")
        p.add_argument("--no-progress", action="store_true", help="Silence progress ticks during evaluation")
        return p.parse_args(argv)

def infer_answers_label_from_dataset(path: Path) -> str | None:
    try:
        with path.open('r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                gen_model = obj.get('gen_model')
                if isinstance(gen_model, str) and gen_model:
                    return gen_model
                # fallback: maybe system message includes model label? skip for now
                break
    except FileNotFoundError:
        return None
    return None

def main(argv: List[str]) -> int:
    args = parse_args(argv)

    # Directory scaffolding based on language & mode
    base_lang_dir = Path("data") / args.language
    training_dir = base_lang_dir / "training_datasets"
    training_evals_dir = training_dir / "evals"
    ft_evals_dir = base_lang_dir / "ft_evals"
    for d in (training_evals_dir, ft_evals_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Infer questions file if not provided
    prefix = "ar_" if args.language == "arabic" else "en_"
    questions_file = args.questions_file or str(base_lang_dir / f"{prefix}eval_questions.txt")
    if not Path(questions_file).exists():
        raise SystemExit(f"Questions file not found: {questions_file}")

    # Determine answers label (may be overridden later if inferred from dataset)
    answers_label = args.answers_label

    # Comparison CSV path resolution
    if args.mode == "dataset":
        default_comp_csv = training_evals_dir / "dataset_eval_comparison.csv"
    else:
        default_comp_csv = ft_evals_dir / "ft_evals_comparison.csv"
    if args.comparison_csv:
        supplied = Path(args.comparison_csv)
        if supplied.is_absolute():
            comparison_csv_path = supplied
        else:
            comparison_csv_path = default_comp_csv.parent / supplied.name
    else:
        comparison_csv_path = default_comp_csv

    # Build judge engine
    engine = EvaluationEngine(model=args.judge_model)
    print(f"[init] Judge model: {args.judge_model}")
    print(f"[init] Language: {args.language} | Mode: {args.mode}")

    # MODE: generation (ft_evals)
    if args.mode.startswith("generate"):
        if not args.gen_model:
            raise SystemExit("--gen-model required for generation modes")
        if not answers_label:
            answers_label = args.gen_model
        # Output dataset naming & placement (always in ft_evals)
        auto_name = f"generated_{'openai' if args.mode=='generate-openai' else 'together'}_{sanitize_filename(args.gen_model)}.jsonl"
        output_dataset_name = args.output_dataset or auto_name
        output_dataset_path = Path(output_dataset_name)
        if not output_dataset_path.is_absolute():
            output_dataset_path = ft_evals_dir / output_dataset_path.name
        dataset_path = Path(
            generate_dataset(
                args.mode,
                questions_file,
                args.gen_model,
                engine,
                str(output_dataset_path),
            )
        )
        print(f"[generate] Dataset ready at {dataset_path}")
    else:  # MODE: dataset
        if not args.dataset:
            raise SystemExit("--dataset required for dataset mode")
        dataset_path = Path(args.dataset)
        if not dataset_path.is_absolute() and not dataset_path.exists():
            # Try resolve inside training_datasets automatically
            candidate = training_dir / dataset_path.name
            if candidate.exists():
                dataset_path = candidate
        if not dataset_path.exists():
            raise SystemExit(f"Dataset not found: {dataset_path}")
        if not answers_label:
            inferred = infer_answers_label_from_dataset(dataset_path)
            if inferred:
                answers_label = inferred
                print(f"[infer] Using inferred answers label: {answers_label}")
            else:
                raise SystemExit("Provide --answers-label (could not infer from dataset).")

    if not answers_label:
        answers_label = 'answers'

    # Load evaluation questions (strict 100)
    eval_questions = load_eval_questions(questions_file, limit=100)
    eval_set: Set[str] = set(eval_questions)
    if len(eval_questions) != 100:
        raise SystemExit(f"Evaluation questions file must contain 100 questions (got {len(eval_questions)}).")

    raw_pairs = load_dataset_pairs(str(dataset_path))
    q_to_a: Dict[str, str] = {}
    for q, a in raw_pairs:
        if q in eval_set and q not in q_to_a:
            q_to_a[q] = a
    missing = [q for q in eval_questions if q not in q_to_a]
    if missing:
        raise SystemExit(f"Dataset missing {len(missing)} required questions. First missing: {missing[:3]}")

    pairs = [(q, q_to_a[q]) for q in eval_questions]
    print(f"[load] Filtered {len(pairs)} evaluation pairs from dataset (strict 100-question set).")

    # Evaluate
    print('[eval] Running evaluation...')
    results = engine.batch_evaluate(pairs, limit=None, progress=not args.no_progress)
    print('[eval] Done.')

    # Aggregate
    aggregated = aggregate_scores(results)
    print('[summary] Aggregated means:')
    for k in sorted(aggregated):
        print(f"  {k}: {aggregated[k]}")

    # Update comparison CSV
    update_comparison_csv(comparison_csv_path, answers_label, aggregated, overwrite=args.overwrite)

    # Results JSONL placement (mode dependent)
    if args.mode == "dataset":
        default_results_dir = training_evals_dir
    else:
        default_results_dir = ft_evals_dir
    default_results_dir.mkdir(parents=True, exist_ok=True)
    if args.results_jsonl:
        supplied = Path(args.results_jsonl)
        if supplied.is_absolute():
            results_jsonl = supplied
        else:
            results_jsonl = default_results_dir / supplied.name
    else:
        filename = f"eval_results_{sanitize_filename(answers_label)}__judged_by_{sanitize_filename(args.judge_model)}.jsonl"
        results_jsonl = default_results_dir / filename

    meta = {
        'dataset': str(dataset_path),
        'answers_label': answers_label,
        'judge_model': args.judge_model,
        'gen_model': args.gen_model,
        'questions_file': questions_file,
        'language': args.language,
        'mode': args.mode,
        'comparison_csv': str(comparison_csv_path),
        'timestamp': dt.now().isoformat(),
    }
    append_results_jsonl(results_jsonl, results, meta)
    print('[done] Completed.')
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
