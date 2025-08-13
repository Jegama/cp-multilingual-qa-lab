<div align="center">
	<img src="./imgs/LogoForHeader.png" alt="Calvinist Parrot" height="140" />
</div>

# Multilingual Reformed Christian Q&A Dataset & Evaluation Toolkit

* **Purpose**: Curate and refine doctrinally faithful, culturally contextual Q&A datasets. 
* **Audience**: Ministries, researchers, model fine‑tuners. 
* **Differentiators**: Reformed theological guardrails, multi‑criteria rubric (adherence, pastoral tone, interfaith sensitivity, linguistic accuracy), multilingual roadmap.
* **Outputs**: Training JSONL, generation/eval scripts, aggregated score matrix, raw judge logs.

Building high‑quality, reformed, multilingual conversational datasets for Calvinist Parrot Ministries.

---

## What This Repo Provides
| Area | Purpose |
|------|---------|
| Data Sources | Curated Arabic (and future English) Christian Q&A from GotQuestions + catechism material. |
| Dataset Builder | `create_dataset_script.py` merges sources and rewrites answers via a controllable ParrotAI chain. |
| Evaluation | `evaluate.py` generates or scores model answers on a fixed 100‑question evaluation set with rubric aggregation. |
| Outputs | Training JSONL (messages format), evaluation comparison CSV, per‑run JSONL judge results. |

---

## Directory Highlights
```
data/
	arabic/
		ar_gotquestions.json          # Raw Arabic structured Q&A (categories + articles)
		ar_qa_catechism.jsonl         # Additional QA pairs (messages schema)
		ar_eval_questions.txt         # EXACTLY 100 evaluation questions (order is canonical)
		ar_training_dataset_*.jsonl   # Previously generated training datasets
	english/ (future expansion)
parrot_ai/                        # Core chain + evaluation engine components
create_dataset_script.py          # Build / enrich training dataset
evaluate.py                       # Unified generation + evaluation CLI
evaluation_comparison.csv         # (Created after first evaluation) aggregated rubric scores
```

---

## Data Schema (Training / Generation JSONL)
Each line: a JSON object with at least:
```jsonc
{
	"messages": [
		{"role": "system", "content": "<system prompt>"},
		{"role": "user", "content": "<question>"},
		{"role": "assistant", "content": "<answer>"}
	],
	"gen_model": "google:gemma-3-7b",          // (present when produced via evaluate.py --mode generate-*)
	"provider": "openai|together|...",          // optional
	"timestamp": "2025-08-13T12:34:56.000000"   // ISO8601
}
```

---

## Environment Setup (Windows examples)
```cmd
python -m venv .venv
".venv\Scripts\activate"
pip install --upgrade pip
pip install -r requirements.txt
```

Optional performance extras (Flash Attention) may require a compatible GPU + toolchain.

### Hugging Face Token (for API mode)
Create a `.env` file:
```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxx
```
Or set via PowerShell / CMD environment before running. Required only when using `--use-api`.

---

## 1. Arabic Training Dataset Creation (`create_dataset_script.py`)
Script pipeline:
1. Load GotQuestions (`ar_gotquestions.json`).
2. Load catechism pairs (`ar_qa_catechism.jsonl`).
3. Combine, then for each pair run the ParrotAI chain to produce a refined answer using the main system prompt.
4. Emit enriched JSONL examples under `data/...`.

### Core Arguments
| Flag | Meaning |
|------|---------|
| `--model` | Base model (local or HF Inference) e.g. `google/gemma-3-12b-it`. |
| `--use-api` | Use HF Inference API instead of local loading. Requires `HF_TOKEN`. |
| `--api-provider` | Provider routing (default `nebius`). |
| `--output` | Target JSONL file. Default `data/temp_training_dataset.jsonl`. |
| `--resume` | Continue appending after existing line count. |
| `--batch-size` | Flush interval (writes every N items). |
| `--max-retries` | Retry count for transient 5xx API errors. |

### Example: API Mode (Recommended for quick start)
```cmd
python create_dataset_script.py ^
	--use-api ^
	--model google/gemma-3-12b-it ^
	--output data/arabic/ar_training_dataset_gemma.jsonl ^
	--batch-size 10
```

### Example: Resume After Interruption
```cmd
python create_dataset_script.py --use-api --model google/gemma-3-12b-it --output data/arabic/ar_training_dataset_gemma.jsonl --resume
```

### Local Model (GPU) Example
```cmd
python create_dataset_script.py --model microsoft/DialoGPT-medium --output data/arabic/ar_training_dataset_local.jsonl
```

On completion, inspect a few lines:
```cmd
more data\arabic\ar_training_dataset_gemma.jsonl
```

---

## 2. Evaluation & Answer Generation (`evaluate.py`)
Capabilities:
1. Evaluate an existing dataset (must cover all 100 questions in `ar_eval_questions.txt`).
2. Generate fresh answers using a provider model (OpenAI‑style or Together API) then evaluate.
3. Aggregate rubric scores into / append a column in `evaluation_comparison.csv`.
4. Append raw per‑question judge outputs into a results JSONL file.

### Rubric Structure
Sections & sub‑criteria (Arabic + ministry context):
- Adherence (Overall)
- Kindness_and_Gentleness (Overall)
- Interfaith_Sensitivity: Respect_and_Handling_Objections, Objection_Acknowledgement, Evangelism, Gospel_Boldness
- Arabic_Accuracy: Grammar_and_Syntax, Theological_Nuance, Contextual_Clarity, Consistency_of_Terms, Arabic_Purity

### Required: 100 Evaluation Questions
`data/arabic/ar_eval_questions.txt` MUST contain exactly 100 lines. Script enforces this.

### Common Workflows
1) Evaluate a prebuilt dataset:
```cmd
python evaluate.py --mode dataset ^
	--dataset data/arabic/ar_training_dataset_gemma.jsonl ^
	--answers-label gemma-12b ^
	--judge-model gpt-5-mini
```

1) Generate answers via OpenAI backend, then evaluate:
```cmd
python evaluate.py --mode generate-openai ^
	--questions-file data/arabic/ar_eval_questions.txt ^
	--gen-model gpt-5-mini ^
	--answers-label gpt-5-mini
```

1) Generate answers via Together API backend, then evaluate:
```cmd
python evaluate.py --mode generate-together ^
	--questions-file data/arabic/ar_eval_questions.txt ^
	--gen-model openai/gpt-oss-120b ^
	--answers-label gpt-oss-120b
```

### Column Overwrite vs. New Suffix
If `answers-label` already exists in `evaluation_comparison.csv`:
* Use `--overwrite` to replace the existing column.
* Omit it to auto‑append with a numeric suffix (e.g., `gemma7_2`).

### Outputs Produced
| File | Description |
|------|-------------|
| `generated_openai_<model>.jsonl` | Auto-named dataset when using generate modes (unless `--output-dataset`). |
| `evaluation_comparison.csv` | Aggregated mean scores per criterion (one column per answers label). |
| `eval_results_<answers>__judged_by_<judge>.jsonl` | Raw line-by-line evaluation records (append-only). |

### Quick Peek at Aggregated Scores
After a run:
```cmd
type evaluation_comparison.csv
```

---

## Typical End-to-End Arabic Flow
```text
1. (Optional) Build / refresh training dataset with create_dataset_script.py
2. Fine-tune or adapt your target model externally using produced JSONL
3. Run evaluate.py --mode dataset on the tuned model's generated dataset
4. Or let evaluate.py generate answers directly, then score them
5. Track progress across models in evaluation_comparison.csv
```

---

## Future: English Expansion
Planned additions:
* Parallel `en_eval_questions.txt` (100 canonical English questions)
* Unified bilingual evaluation matrix
* Cross-lingual consistency scoring (e.g., doctrinal alignment across languages)

---

## Roadmap (Language Expansion Focus)
Near Term (English):
* Add `data/english/` parity: ensure `en_gotquestions.json`, `en_qa_catechism.jsonl`, and canonical `en_eval_questions.txt` (100 questions) are finalized and documented.
* Run first English baseline evaluations using existing rubric (temporary direct reuse) and note any rubric wording needing neutral language adjustments.
* Update scripts (if needed) to auto-detect `--lang en` via file path conventions.

Mid Term (Spanish):
* Introduce `data/spanish/` with `es_gotquestions.json`, `es_qa_catechism.jsonl`, `es_eval_questions.txt` (100 questions).
* Light rubric localization (tone & cultural sensitivity phrasing) while keeping scoring math identical.
* Add language tag columns in `evaluation_comparison.csv` (naming: `<label> (ar)`, `<label> (en)`, `<label> (es)`).
* Implement optional cross-language doctrinal consistency diff (start with Arabic ↔ English, then include Spanish).

Long Term / Community Help Wanted:
* Additional languages (e.g., Chinese, Hindi, French, Bengali, Portuguese, Russian, Urdu) — contributors provide: (1) legally usable Q&A sources, (2) 100-question eval set, (3) initial rubric translation notes.
* Automated doctrinal drift detection across languages.
* Optional citation grounding (Scripture + source attribution) layer.

If you'd like to help with a new language: open an issue proposing (1) language, (2) source legality/permissions, (3) draft 100 evaluation questions, (4) rubric adaptation considerations.

---

## Contributing
Internal use for now. Feel free to open issues / suggestions (naming, rubric refinement, additional criteria for English).

---

## Contact
For questions or support, please [reach out](mailto:jesusmancilla@calvinistparrotministries.org).

# Soli Deo Gloria

**"For from Him and through Him and to Him are all things. To Him be the glory forever! Amen."**
- Romans 11:36

[Copy.church](https://copy.church/explain/importance/) | [sellingJesus.org](https://sellingJesus.org/free)
---|---
![Copy.church](https://copy.church/badges/lcc_alt_pde.png) | ![sellingJesus.org/free](https://copy.church/badges/sj_standard_pd.png)

