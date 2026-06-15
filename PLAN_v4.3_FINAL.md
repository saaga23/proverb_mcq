# ProverbGap v4.3 — FINAL IMPLEMENTATION PLAN
## Last Kaggle Upload Before Scale-Ready

**Status**: Research complete. 8-agent audit done. Accredited solutions mapped.
**Goal**: One more notebook upload → clean N=50 run → ready to shard N=700.

---

## ACCREDITED SOLUTIONS MAP

| Problem | Accredited Source | Solution Pattern |
|---------|-------------------|------------------|
| CoT broken (52.7%) | MMLU-Pro (Wang et al., 2024); SKYLENAGE; DISSECT; Chain-of-Reasoning (Tsinghua) | Multi-stage regex: `answer is (X)` → `Answer: (X)` → `\boxed{X}` → last `[A-D]` |
| S2 fallback > S1 | Alhazmi et al. EMNLP 2024 Survey; ADQAB (Zhang et al., 2025) | Drop fallback from headline metric; report S2-strict only; add BERTScore validation |
| Semantic duplicates | Alhazmi et al. 2024; Joint DG (FlanT5, 2025) | Embed-based dedup (MiniLM-L6-v2) + inter-distractor similarity ceiling |
| Contamination | Sainz et al. 2023; Deng et al. 2024; Jacovi et al. 2023 | Paraphrase drop test (Allam: 99.1%→77.8% = leakage); fuzzy n-gram filter |
| Circuit breaker | Production SRE pattern (Netflix Hystrix) | 3 failures → 60s cooldown → 1 retry → permanent skip |
| GPU deps | bitsandbytes standard (accepted across HF) | `pip install -U bitsandbytes>=0.46.1` + smoke test |
| Checkpoint I/O | SQLite WAL mode standard | WAL mode + background thread flush |
| Position bias | Gupta et al. 2024 (MMLU answer reordering drops 13%) | Stratified per-model analysis + balanced position allocation |

---

## PHASE 0: OVERHEAD THAT CAN FAIL (Spot Before Start)

**Agent: 1 self-check agent**

1. **Kaggle secrets present?** GROQ_API_KEY, NVIDIA_API_KEY, HF_TOKEN
2. **AfroLLaMA license accepted?** huggingface.co/Jacaranda/AfroLlama_V1
3. **GPU enabled?** T4 selected
4. **Internet access enabled?** Required for API calls + HF downloads
5. **Data path valid?** `/kaggle/input/.../Yoruba_cleaned.csv` exists
6. **Disk space?** 20GB+ free for models + outputs

---

## PHASE 1: CRITICAL FIXES (P0 — Must Have)

### 1.1 CoT Answer Extraction Fix
**Source**: MMLU-Pro (Wang et al., 2024) + DISSECT + Chain-of-Reasoning

Current code (broken):
```python
_RE_ANSWER_LETTER = re.compile(r'\b([A-D])\b')
```

Accredited fix (multi-stage, ordered by specificity):
```python
_COT_PATTERNS = [
    re.compile(r'answer\s*is\s*\(?([A-D])\)?', re.I),      # MMLU-Pro primary
    re.compile(r'Answer:\s*([A-D])', re.I),                  # MMLU-Pro secondary
    re.compile(r'\boxed\{([A-D])\}', re.I),                  # Chain-of-Reasoning
    re.compile(r'FINAL\s*ANSWER:\s*([A-D])', re.I),          # DISSECT
    re.compile(r'\b([A-D])\b'),                              # Last resort
]

def extract_answer(text):
    for pat in _COT_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(1).upper()
    return None
```

Also fix `SYS_COT` prompt to explicitly require "Answer: X" on last line:
```python
SYS_COT = (
    "You are a blind evaluator taking a multiple-choice test.\n"
    "Think step by step, then write your final answer on the LAST line as:\n"
    "Answer: X\n"
    "where X is exactly one letter: A, B, C, or D."
)
```

**File**: Cell 7 (Evaluation Prompts)

### 1.2 Drop S2-Pipeline Headline Metric
**Source**: Alhazmi et al. EMNLP 2024 Survey — "no gold standard for evaluating distractors"

Current code reports:
- S1: 80.9%
- S2-pipeline: 67.9% ← MIXES strict + fallback
- S2-strict: 63.2%
- S2-fallback: 83.5% ← HIGHER than S1

Accredited fix: Report ONLY these:
- S1 (baseline)
- S2-strict (true paraphrase challenge)
- S2-fallback rate (pipeline quality metric, NOT accuracy)
- Drop "S2-pipeline" entirely from headline results

**File**: Cell 12 (main() results print)

### 1.3 Circuit Breaker for Llama-4-Maverick
**Source**: Production SRE pattern (Netflix Hystrix) — after 3 failures, pause 60s

Current: 22 errors on same model, no circuit breaker, retry storms stall pipeline.

Accredited fix:
```python
_model_failures = {}
_model_failure_lock = threading.Lock()
MODEL_CIRCUIT_THRESHOLD = 3
MODEL_CIRCUIT_COOLDOWN = 60

def is_model_circuit_open(model_name):
    with _model_failure_lock:
        if model_name not in _model_failures:
            return False
        fails, last_fail = _model_failures[model_name]
        if fails >= MODEL_CIRCUIT_THRESHOLD:
            if time.time() - last_fail < MODEL_CIRCUIT_COOLDOWN:
                return True
            else:
                _model_failures[model_name] = (0, 0)
                return False
    return False

def record_model_failure(model_name):
    with _model_failure_lock:
        fails, _ = _model_failures.get(model_name, (0, 0))
        _model_failures[model_name] = (fails + 1, time.time())
```

In `eval_worker`, before evaluating, check `is_model_circuit_open(model)` and skip with logged warning.

**File**: Cell 3 (API Infrastructure) + Cell 11 (eval_worker)

### 1.4 bitsandbytes + GPU Smoke Test
**Source**: HuggingFace standard practice

Add at notebook start (Cell 1 or 2):
```python
# Pre-flight GPU dependency check
if torch.cuda.is_available():
    try:
        import bitsandbytes
        print(f"[GPU] bitsandbytes {bitsandbytes.__version__} OK")
    except ImportError:
        print("[GPU] Installing bitsandbytes...")
        !pip install -U bitsandbytes>=0.46.1 -q
        import bitsandbytes
    
    # 60-second smoke test
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
        tok = AutoTokenizer.from_pretrained("bert-base-uncased")
        print("[GPU] Smoke test PASSED")
    except Exception as e:
        print(f"[GPU] Smoke test FAILED: {e}")
```

**File**: New cell after imports, before main

### 1.5 HF Token Plumbing for Gated Models
**Source**: HuggingFace auth standard

Current: `HF_TOKEN` set in env but not passed to `from_pretrained()`.

Fix: In `evaluate_gpu_models()`, add `token=HF_TOKEN` to all `from_pretrained()` calls:
```python
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True, token=HF_TOKEN)
model = AutoModelForCausalLM.from_pretrained(model_id, token=HF_TOKEN, **load_kwargs)
```

**File**: Cell 9 (GPU Local Models)

---

## PHASE 2: MAJOR FIXES (P1 — Strongly Recommended)

### 2.1 S2 Semantic Duplicate Detection
**Source**: Alhazmi et al. EMNLP 2024 + Joint DG (FlanT5, 2025)

Current: No semantic dedup. Options like "Laugh and grow fat" → 4 nearly identical paraphrases.

Accredited fix: Post-generation, compute pairwise cosine similarity between all 4 options. If any pair > 0.85 (MiniLM-L6-v2), regenerate.

```python
from sentence_transformers import SentenceTransformer
_dedup_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

_MAX_SIM = 0.85

def has_semantic_duplicates(options):
    if len(options) < 2:
        return False
    embs = _dedup_model.encode(options, convert_to_tensor=True)
    sims = cosine_similarity(embs.cpu().numpy())
    for i in range(len(options)):
        for j in range(i+1, len(options)):
            if sims[i][j] > _MAX_SIM:
                return True
    return False
```

**File**: Cell 5 (Strategy 2 generation)

### 2.2 Yoruba S2 Few-Shot Prompt
**Source**: Maity et al. ECIR 2024 (Multi-Stage Prompting for Hindi/Bengali)

Current: Zero-shot S2 prompt fails on 46% of Yoruba proverbs.

Fix: Add 1-2 Yoruba examples in the S2 system prompt showing desired paraphrase + distractor format.

**File**: Cell 5 (Strategy 2 prompt)

### 2.3 Checkpoint Background Thread + WAL
**Source**: SQLite WAL mode standard

Current: Synchronous checkpoint writes stall main thread 20-77s.

Fix:
```python
# In APICache.__init__
self.conn.execute('PRAGMA journal_mode=WAL')

# In main(), run checkpoint in background
def _bg_checkpoint(results, path):
    pd.DataFrame(results).to_csv(path, index=False)

def save_checkpoint():
    if results:
        t = threading.Thread(target=_bg_checkpoint, args=(results.copy(), OUT_DIR / 'evaluation_results_partial.csv'))
        t.start()
```

**File**: Cell 3 (APICache) + Cell 12 (main)

### 2.4 Allam Leakage Formal Detection
**Source**: Sainz et al. 2023; Deng et al. 2024; Jacovi et al. 2023

Current: Manual flagging. Need automated heuristic.

Fix: In analysis, auto-flag any model where:
- S1 accuracy >= 95% AND S1-S2 drop >= 20pp → "HIGH leakage risk"
- S1 accuracy >= 90% AND S1-S2 drop >= 15pp → "MEDIUM leakage risk"

Exclude HIGH risk models from primary aggregates. Report separately.

**File**: Cell 12 (analysis section)

### 2.5 Position Bias Stratified Analysis
**Source**: Gupta et al. 2024 (MMLU answer reordering drops 13%)

Current: Chi² pools all models, underpowered.

Fix: Report position bias PER MODEL (not pooled):
```python
for model in COMMITTEE_MODELS:
    # Chi² for this model only, all styles pooled
    # If any model shows p<0.05, flag as significant
```

**File**: Cell 12 (analysis section)

### 2.6 AfriBERTa Pooler Fix
**Source**: Standard transformer loading practice

Current: MISSING pooler.dense.* → random init.

Fix: Use mean pooling instead of CLS token:
```python
# In evaluate_encoder
emb = outputs.last_hidden_state.mean(dim=1)  # mean of all tokens
```

**File**: Cell 8 (Encoder Baselines)

---

## PHASE 3: SCALE PREPARATION (P1 — For N=700)

### 3.1 Runtime Projection + Auto-Throttle
At notebook start, project runtime:
```python
projected_hours = (
    (PILOT_N * 3 * 0.5 / 60) +          # S2 generation (min)
    (PILOT_N * 3 * 3 * 2 * 4 / 3600) +  # API eval (hours, 4s/req)
    (PILOT_N * 3 * 2 * 0.5 / 3600) +    # Encoder (hours)
    0.5                                  # overhead
)
print(f"[PROJECTION] Estimated runtime: {projected_hours:.1f}h")
if projected_hours > 8.5:
    print("[WARNING] Exceeds Kaggle 9h limit. Reduce PILOT_N or shard.")
```

### 3.2 Sharding Strategy (if N=700)
If user sets PILOT_N > 300, warn and suggest:
```
For N=700, run 4 notebooks:
- Notebook 1: English (N=700)
- Notebook 2: Arabic (N=700)
- Notebook 3: Yoruba (N=700)
- Notebook 4: Analysis (merge CSVs)
```

### 3.3 S2 Parallel Generation
Current: Sequential API calls.
Fix: Use ThreadPoolExecutor(5) for S2 generation, one thread per Groq key.

---

## PHASE 4: VALIDATION (Final Check Before Upload)

### 4.1 Syntax Check
```bash
python3 -m py_compile proverbgap_kaggle_final.py
```

### 4.2 Notebook JSON Check
```python
import json
json.load(open('proverbgap_kaggle_final.ipynb'))
```

### 4.3 Module Init Check
```python
exec(open('proverbgap_kaggle_final.py').read().replace("if __name__", "if False"))
```

### 4.4 Figure Generation Dry-Run
Create dummy CSVs and run `generate_figures()` locally.

---

## EXECUTION ORDER (For New Chat)

1. **Agent A**: Implement Phase 1.1 (CoT fix) + Phase 1.2 (metric drop)
2. **Agent B**: Implement Phase 1.3 (circuit breaker) + Phase 1.4 (bitsandbytes) + Phase 1.5 (HF token)
3. **Agent C**: Implement Phase 2.1 (semantic dedup) + Phase 2.2 (Yoruba few-shot)
4. **Agent D**: Implement Phase 2.3 (checkpoint) + Phase 2.4 (leakage heuristic) + Phase 2.5 (position bias) + Phase 2.6 (AfriBERTa)
5. **Agent E**: Implement Phase 3 (scale prep)
6. **Agent F**: Phase 4 validation (syntax, JSON, init, figures)
7. **Agent G**: Final diff review — compare v4.2 → v4.3
8. **Agent H**: Memory update + upload instructions

---

## FILES TO MODIFY

| File | Cells Modified |
|------|----------------|
| `proverbgap_kaggle_final.py` | All (regenerate `.ipynb`) |
| Cell 1 (Config) | Add PILOT_N warning, runtime projection |
| Cell 2 (API Infra) | Add circuit breaker, WAL mode, HF_TOKEN global |
| Cell 5 (S2 Gen) | Add semantic dedup, Yoruba few-shot, parallel generation |
| Cell 7 (Eval) | Fix CoT prompt, multi-stage extract_answer |
| Cell 8 (Encoders) | AfriBERTa mean pooling |
| Cell 9 (GPU) | bitsandbytes smoke test, token=HF_TOKEN |
| Cell 12 (Main) | Drop S2-pipeline headline, add leakage heuristic, stratified position bias |

---

## ACCREDITED CITATIONS FOR PAPER

- **CoT extraction**: Wang et al., MMLU-Pro; DISSECT; Chain-of-Reasoning (Tsinghua)
- **Distractor quality**: Alhazmi et al., EMNLP 2024 Survey
- **Contamination**: Sainz et al. 2023; Deng et al. 2024; Jacovi et al. 2023
- **Position bias**: Gupta et al. 2024
- **Low-resource prompting**: Maity et al., ECIR 2024
- **BERTScore**: Joint DG (FlanT5, 2025)
