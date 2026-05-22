### 1. System Prompt (v1.0) with GPT-5 Mini Judge

```bash
# Google Gemini 3 Flash
python cp_eval_llms.py --language english --mode generate-api_evals --provider google --gen-model gemini-3-flash-preview --answers-label google-gemini-3-flash-v1_0 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_0 --limit 0

# OpenAI GPT-5 Mini
python cp_eval_llms.py --language english --mode generate-api_evals --provider openai --gen-model gpt-5-mini --answers-label openai-gpt-5-mini-v1_0 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_0 --limit 0

# xAI Grok 4.1 Fast
python cp_eval_llms.py --language english --mode generate-api_evals --provider xai --gen-model grok-4-1-fast-reasoning --answers-label xai-grok-4-1-fast-v1_0 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_0 --limit 0

# Anthropic Claude Haiku 4.5
python cp_eval_llms.py --language english --mode generate-api_evals --provider anthropic --gen-model claude-haiku-4-5-20251001 --answers-label anthropic-claude-haiku-4-5-v1_0 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_0 --limit 0
```

### 2. Vanilla (Baseline) with GPT-5 Mini Judge

```bash
# Google Gemini 3 Flash
python cp_eval_llms.py --language english --mode generate-api_evals --provider google --gen-model gemini-3-flash-preview --answers-label google-gemini-3-flash-vanilla --judge-model gpt-5-mini --system-prompt-label baseline --limit 0

# OpenAI GPT-5 Mini
python cp_eval_llms.py --language english --mode generate-api_evals --provider openai --gen-model gpt-5-mini --answers-label openai-gpt-5-mini-vanilla --judge-model gpt-5-mini --system-prompt-label baseline --limit 0

# xAI Grok 4.1 Fast
python cp_eval_llms.py --language english --mode generate-api_evals --provider xai --gen-model grok-4-1-fast-reasoning --answers-label xai-grok-4-1-fast-vanilla --judge-model gpt-5-mini --system-prompt-label baseline --limit 0

# Anthropic Claude Haiku 4.5
python cp_eval_llms.py --language english --mode generate-api_evals --provider anthropic --gen-model claude-haiku-4-5-20251001 --answers-label anthropic-claude-haiku-4-5-vanilla --judge-model gpt-5-mini --system-prompt-label baseline --limit 0
```

### 3. System Prompt (v1.0) with Gemini 3 Flash Judge

```bash
# Google Gemini 3 Flash (Judged by Gemini 3)
python cp_eval_llms.py --language english --mode dataset --dataset data/english/api_evals/generated_api_google_google-gemini-3-flash-v1_0.jsonl --judge-model gemini-3-flash-preview --answers-label google-gemini-3-flash-v1_0-2 --limit 0

# OpenAI GPT-5 Mini (Judged by Gemini 3)
python cp_eval_llms.py --language english --mode dataset --dataset data/english/api_evals/generated_api_openai_openai-gpt-5-mini-v1_0.jsonl --judge-model gemini-3-flash-preview --answers-label openai-gpt-5-mini-v1_0-2 --limit 0

# xAI Grok 4.1 Fast (Judged by Gemini 3)
python cp_eval_llms.py --language english --mode dataset --dataset data/english/api_evals/generated_api_xai_xai-grok-4-1-fast-v1_0.jsonl --judge-model gemini-3-flash-preview --answers-label xai-grok-4-1-fast-v1_0-2 --limit 0

# Anthropic Claude Haiku 4.5 (Judged by Gemini 3)
python cp_eval_llms.py --language english --mode dataset --dataset data/english/api_evals/generated_api_anthropic_anthropic-claude-haiku-4-5-v1_0.jsonl --judge-model gemini-3-flash-preview --answers-label anthropic-claude-haiku-4-5-v1_0-2 --limit 0
```

### 4. System Prompt (v1.1) with GPT-5 Mini Judge

```bash
# Google Gemini 3 Flash
python cp_eval_llms.py --language english --mode generate-api_evals --provider google --gen-model gemini-3-flash-preview --answers-label google-gemini-3-flash-v1_1 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_1 --limit 0

# OpenAI GPT-5 Mini
python cp_eval_llms.py --language english --mode generate-api_evals --provider openai --gen-model gpt-5-mini --answers-label openai-gpt-5-mini-v1_1 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_1 --limit 0

# xAI Grok 4.1 Fast
python cp_eval_llms.py --language english --mode generate-api_evals --provider xai --gen-model grok-4-1-fast-reasoning --answers-label xai-grok-4-1-fast-v1_1 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_1 --limit 0

# Anthropic Claude Haiku 4.5
python cp_eval_llms.py --language english --mode generate-api_evals --provider anthropic --gen-model claude-haiku-4-5-20251001 --answers-label anthropic-claude-haiku-4-5-v1_1 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_1 --limit 0
```

### 5. System Prompt (v1.2) with GPT-5 Mini Judge

```bash
# Google Gemini 3 Flash
python cp_eval_llms.py --language english --mode generate-api_evals --provider google --gen-model gemini-3-flash-preview --answers-label google-gemini-3-flash-v1_2 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_2 --limit 0

# OpenAI GPT-5 Mini
python cp_eval_llms.py --language english --mode generate-api_evals --provider openai --gen-model gpt-5-mini --answers-label openai-gpt-5-mini-v1_2 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_2 --limit 0

# xAI Grok 4.1 Fast
python cp_eval_llms.py --language english --mode generate-api_evals --provider xai --gen-model grok-4-1-fast-reasoning --answers-label xai-grok-4-1-fast-v1_2 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_2 --limit 0

# Anthropic Claude Haiku 4.5
python cp_eval_llms.py --language english --mode generate-api_evals --provider anthropic --gen-model claude-haiku-4-5-20251001 --answers-label anthropic-claude-haiku-4-5-v1_2 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_2 --limit 0
```

### 6. System Prompt (v1.3) with GPT-5 Mini Judge

```bash
# Google Gemini 3 Flash
python cp_eval_llms.py --language english --mode generate-api_evals --provider google --gen-model gemini-3-flash-preview --answers-label google-gemini-3-flash-v1_3 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_3 --limit 0

# OpenAI GPT-5 Mini
python cp_eval_llms.py --language english --mode generate-api_evals --provider openai --gen-model gpt-5-mini --answers-label openai-gpt-5-mini-v1_3 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_3 --limit 0

# xAI Grok 4.1 Fast
python cp_eval_llms.py --language english --mode generate-api_evals --provider xai --gen-model grok-4-1-fast-reasoning --answers-label xai-grok-4-1-fast-v1_3 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_3 --limit 0

# Anthropic Claude Haiku 4.5
python cp_eval_llms.py --language english --mode generate-api_evals --provider anthropic --gen-model claude-haiku-4-5-20251001 --answers-label anthropic-claude-haiku-4-5-v1_3 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_3 --limit 0
```

### 7. System Prompt (v1.4) with GPT-5 Mini Judge

```bash
# Google Gemini 3 Flash
python cp_eval_llms.py --language english --mode generate-api_evals --provider google --gen-model gemini-3-flash-preview --answers-label google-gemini-3-flash-v1_4 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_4 --limit 0

# Google Gemini 3.1 Flash Lite
python cp_eval_llms.py --language english --mode generate-api_evals --provider google --gen-model gemini-3.1-flash-lite --answers-label google-gemini-3-1-flash-lite-v1_4 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_4 --limit 0

# Google Gemini 3.5 Flash
python cp_eval_llms.py --language english --mode generate-api_evals --provider google --gen-model gemini-3.5-flash --answers-label google-gemini-3-5-flash-v1_4 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_4 --limit 0

# OpenAI GPT-5 Mini
python cp_eval_llms.py --language english --mode generate-api_evals --provider openai --gen-model gpt-5-mini --answers-label openai-gpt-5-mini-v1_4 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_4 --limit 0

# OpenAI GPT-5.4 Mini
python cp_eval_llms.py --language english --mode dataset --dataset data/english/api_evals/generated_api_openai_openai-gpt-5.4-mini-v1_4.jsonl --judge-model gpt-5-mini --answers-label openai-gpt-5.4-mini-v1_4-2 --system-prompt-label v1_4 --limit 0

# xAI Grok 4.1 Fast
python cp_eval_llms.py --language english --mode generate-api_evals --provider xai --gen-model grok-4-1-fast-reasoning --answers-label xai-grok-4-1-fast-v1_4 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_4 --limit 0

# xAI Grok 4.3
python cp_eval_llms.py --language english --mode generate-api_evals --provider xai --gen-model grok-4.3 --answers-label xai-grok-4.3-v1_4 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_4 --limit 0

# Anthropic Claude Haiku 4.5
python cp_eval_llms.py --language english --mode generate-api_evals --provider anthropic --gen-model claude-haiku-4-5-20251001 --answers-label anthropic-claude-haiku-4-5-v1_4 --judge-model gpt-5-mini --use-system-prompt --system-prompt-label v1_4 --limit 0
```

### 8. System Prompt (v1.4) with GPT-5.4 Mini Judge

```bash
# OpenAI GPT-5.4 Mini
python cp_eval_llms.py --language english --mode generate-api_evals --provider openai --gen-model gpt-5.4-mini --answers-label openai-gpt-5.4-mini-v1_4 --judge-model gpt-5.4-mini --use-system-prompt --system-prompt-label v1_4 --limit 0

# OpenAI GPT-5 Mini (Judged by GPT-5.4 Mini)
python cp_eval_llms.py --language english --mode dataset --dataset data/english/api_evals/generated_api_openai_openai-gpt-5-mini-v1_4.jsonl --judge-model gpt-5.4-mini --answers-label openai-gpt-5-mini-v1_4-2 --system-prompt-label v1_4 --limit 0

# Google Gemini 3 Flash
python cp_eval_llms.py --language english --mode dataset --dataset data/english/api_evals/generated_api_google_google-gemini-3-flash-v1_4.jsonl --judge-model gpt-5.4-mini --answers-label google-gemini-3-flash-v1_4-2 --system-prompt-label v1_4 --limit 0

# xAI Grok 4.1 Fast
python cp_eval_llms.py --language english --mode dataset --dataset data/english/api_evals/generated_api_xai_xai-grok-4-1-fast-v1_4.jsonl --judge-model gpt-5.4-mini --answers-label xai-grok-4-1-fast-v1_4-2 --system-prompt-label v1_4 --limit 0

# Anthropic Claude Haiku 4.5
python cp_eval_llms.py --language english --mode dataset --dataset data/english/api_evals/generated_api_anthropic_anthropic-claude-haiku-4-5-v1_4.jsonl --judge-model gpt-5.4-mini --answers-label anthropic-claude-haiku-4-5-v1_4-2 --system-prompt-label v1_4 --limit 0
```
