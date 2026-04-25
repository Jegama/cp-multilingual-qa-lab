# Frozen state — Arabic LLM-as-judge paper

**Commit:** c50ef76
**Tag:** paper-v1
**Branch:** paper-frozen
**Frozen on:** 2026-04-25T20:35:21Z

This branch is immutable. It corresponds to the experiments reported in
`A Judge-Centric Pipeline for Scalable Multilingual QA Evaluation without
Native Experts: An Arabic Case Study`.

Reviewer entry points:
- Canonical eval list: `data/arabic/ar_eval_questions.txt`
- Training JSONL: `data/arabic/training_datasets/ar_training_dataset_gemma-3-27b.jsonl`
- Aggregated results: `data/arabic/{training_datasets/evals,ft_evals,api_evals}/*_comparison.csv`
- Master prompt: `resources/Arabic Master Prompt.md`
- Eval framework: `resources/Arabic Evaluation Framework.md`
- Reproducibility supplement: see paper-handoff/supplement/ (out-of-tree).

Newer prompt revisions and additional providers (English Master Prompt v1.4,
sermon-eval pipeline, Anthropic / Gemini-3 / gpt-5.4-mini) live on `master`
and are not part of this paper.
