import os
import sys
import json
import time
import hashlib
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List, Tuple

try:
    import pandas as pd
except ImportError:
    print("pandas not found; install: pip install pandas")
    sys.exit(1)


ANNOTATION_PROMPT_TEMPLATE = """You are an expert annotator for proverb understanding.
Given the following proverb and four candidate meanings, select the ONE correct meaning.

Proverb: {proverb}
Options:
A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}

Think step by step about which meaning is correct. After your reasoning, respond with ONLY a single letter (A, B, C, or D). Do not include any other text."""

# Open-weight models used as LLM-annotator proxies.
# Includes a reasoning model (DeepSeek-R1-Distill-Qwen-32B) for reviewer methodological rigor.
DEFAULT_MODAL_MODELS = [
    "Qwen/Qwen2.5-7B-Instruct",
    "microsoft/Phi-3.5-mini-instruct",
    "meta-llama/Llama-3.2-3B-Instruct",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
]

OUTPUT_DIR = "annotation/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
LOG_PATH = os.path.join(OUTPUT_DIR, "modal_annotator_log.jsonl")


def _redact(text: str) -> str:
    if not isinstance(text, str):
        return text
    return re.sub(r"(sk-|api[_-]?key|token|secret)\s*[:=]\s*\S+", r"\1=***REDACTED***", text, flags=re.IGNORECASE)


def _load_hf_token() -> Optional[str]:
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if not token and Path(".env").exists():
        for line in Path(".env").read_text(encoding="utf-8").splitlines():
            if line.strip().startswith(("HF_TOKEN=", "HUGGING_FACE_HUB_TOKEN=")):
                token = line.split("=", 1)[1].strip().strip("\"'")
                break
    return token


def _load_env_token() -> Optional[str]:
    token = os.environ.get("MODAL_TOKEN") or os.environ.get("MODAL_API_TOKEN")
    if not token and Path(".env").exists():
        for line in Path(".env").read_text(encoding="utf-8").splitlines():
            if line.strip().startswith(("MODAL_TOKEN=", "MODAL_API_TOKEN=")):
                token = line.split("=", 1)[1].strip().strip("\"'")
                break
    return token


def _estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    return 0.0


def _extract_answer(text: str) -> Optional[str]:
    if not text:
        return None
    text = str(text).strip()
    matches = re.findall(r'\b([ABCD])\b', text, re.IGNORECASE)
    if matches:
        return matches[-1].upper()
    boxed = re.findall(r'\\boxed\{([ABCD])\}', text, re.IGNORECASE)
    if boxed:
        return boxed[-1].upper()
    return None


def _log(record: Dict) -> None:
    record = dict(record)
    for k in ("prompt", "response", "error"):
        if isinstance(record.get(k), str):
            record[k + "_hash"] = hashlib.sha256(record[k].encode()).hexdigest()[:16]
            record[k] = _redact(record[k])
    record["timestamp"] = datetime.now(timezone.utc).isoformat()
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Modal inference: one App + image per model, vLLM engine, persistent HF cache
# ---------------------------------------------------------------------------
try:
    import modal

    # Persistent HuggingFace cache volume so weights download once and are
    # reused across cold starts / model switches.
    _HF_VOLUME = modal.Volume.from_name("hf-model-cache")
    _HF_MOUNT = "/hf-cache"
    _HF_ENV = {"HF_HOME": _HF_MOUNT, "TRANSFORMERS_CACHE": _HF_MOUNT}

    # Proven image spec from the working Lemons pipeline:
    #   - debian_slim base avoids poisoned PyTorch-CUDA build cache
    #   - vLLM 0.6.3.post1 + transformers 4.45.2 avoids Qwen2.5 tokenizer bugs
    def _make_image() -> "modal.Image":
        return (
            modal.Image.debian_slim(python_version="3.10")
            .pip_install(
                "vllm==0.6.3.post1",
                "transformers==4.45.2",
                "huggingface_hub",
            )
            .run_commands([
                "python -c \"import torch, transformers, vllm; print('build_ok')\"",
            ])
        )

    # Shared vLLM runner; one function per model so Modal creates one container
    # per model. This avoids VRAM fragmentation and the hangs we saw when
    # loading multiple large models in the same process.
    def _run_vllm_batch(model: str, prompts: List[str]) -> List[str]:
        from vllm import LLM, SamplingParams
        from huggingface_hub import login

        _hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
        if _hf_token:
            login(token=_hf_token, add_to_git_credential=False)

        is_reasoning = "DeepSeek-R1" in model or "deepseek-reasoner" in model.lower()
        max_tokens = 512 if is_reasoning else 256

        llm = LLM(
            model=model,
            tensor_parallel_size=1,
            gpu_memory_utilization=0.90,
            dtype="bfloat16",
            trust_remote_code=True,
            enforce_eager=False,
            max_model_len=4096,
        )

        sampling_params = SamplingParams(
            temperature=0.0,
            max_tokens=max_tokens,
            repetition_penalty=1.1,
        )

        outputs = llm.generate(prompts, sampling_params)
        return [o.outputs[0].text.strip() for o in outputs]

    # One App per model with its own image and cached HF volume.
    _APPS: Dict[str, Tuple[str, object]] = {}

    _hf_token = _load_hf_token()
    _hf_secret = []
    if _hf_token and _hf_token.startswith("hf_") and len(_hf_token) > 30:
        _hf_secret = [modal.Secret.from_dict({"HF_TOKEN": _hf_token})]

    for _model in DEFAULT_MODAL_MODELS:
        _app_name = f"proverbgap-annotator-{_model.replace('/', '-').replace('.', '-')}"
        _app = modal.App(
            _app_name,
            image=_make_image(),
        )

        @_app.function(
            gpu="A100",
            timeout=1800,
            retries=1,
            volumes={_HF_MOUNT: _HF_VOLUME},
            secrets=_hf_secret + [modal.Secret.from_dict(_HF_ENV)],
        )
        def _batch(model: str = _model, prompts: List[str] = []) -> List[str]:
            return _run_vllm_batch(model, prompts)

        _APPS[_model] = (_app, _batch)

    _REGISTRY: Dict[str, Tuple[object, object]] = {m: (v[0], v[1]) for m, v in _APPS.items()}

except Exception as exc:
    _REGISTRY = {}
    _MODAL_BUILD_ERROR = exc


def annotate_item_modal(
    validation_id: str,
    proverb: str,
    options: Dict[str, str],
    language: str,
    model_name: str,
    response_text: Optional[str] = None,
) -> Dict:
    prompt = ANNOTATION_PROMPT_TEMPLATE.format(
        proverb=proverb,
        option_a=options.get("A", ""),
        option_b=options.get("B", ""),
        option_c=options.get("C", ""),
        option_d=options.get("D", ""),
    )
    if response_text is None:
        return {
            "validation_id": validation_id,
            "language": language,
            "model": model_name,
            "answer": None,
            "confidence": None,
            "latency_ms": None,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "cost_usd": 0.0,
            "finish_reason": "skipped",
            "errors": "no response provided (inference not executed)",
        }

    answer = _extract_answer(response_text)
    record = {
        "run_id": os.environ.get("ANNOTATION_RUN_ID", "modal_manual"),
        "validation_id": validation_id,
        "language": language,
        "model": model_name,
        "prompt": prompt,
        "response": response_text,
        "finish_reason": "ok" if answer else "parse_failed",
        "errors": "" if answer else f"Failed to extract A/B/C/D from: {response_text!r}",
    }
    _log(record)
    return {
        "validation_id": validation_id,
        "language": language,
        "model": model_name,
        "answer": answer,
        "confidence": None,
        "latency_ms": None,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "cost_usd": 0.0,
        "finish_reason": record["finish_reason"],
        "errors": record["errors"],
    }


def run_modal_annotation(
    csv_path: str,
    output_dir: str = OUTPUT_DIR,
    models: Optional[List[str]] = None,
    max_items: Optional[int] = None,
    gpu: str = "A100",
) -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(csv_path)
    if max_items:
        df = df.head(max_items)
    models = models or DEFAULT_MODAL_MODELS

    if not _REGISTRY:
        raise RuntimeError(
            f"Modal apps unavailable (build error: {getattr(_MODAL_BUILD_ERROR, 'args', _MODAL_BUILD_ERROR)}); "
            "cannot run live Modal annotation."
        )

    run_id = f"modal_annotator_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    os.environ["ANNOTATION_RUN_ID"] = run_id

    rows = []
    for _, row in df.iterrows():
        rows.append({
            "vid": str(row.get("validation_id", row.get("mcq_id", ""))),
            "language": str(row.get("language", "")),
            "proverb": str(row.get("proverb", "")),
            "options": {k: str(row.get(f"option_{k}", row.get(k, ""))) for k in ("A", "B", "C", "D")},
        })

    prompts = [
        ANNOTATION_PROMPT_TEMPLATE.format(
            proverb=r["proverb"],
            option_a=r["options"].get("A", ""),
            option_b=r["options"].get("B", ""),
            option_c=r["options"].get("C", ""),
            option_d=r["options"].get("D", ""),
        )
        for r in rows
    ]

    results: List[Dict] = []
    for model in models:
        entry = _REGISTRY.get(model)
        if entry is None:
            print(f"[skip] no baked image for {model}; add it to _APPS to enable.")
            continue
        app, fn = entry
        t0 = time.time()
        try:
            with app.run():
                responses = fn.remote(model, prompts)
        except Exception as exc:
            print(f"[error] {model} failed: {exc}")
            responses = [""] * len(prompts)
        elapsed = (time.time() - t0) * 1000
        per_item_ms = round(elapsed / max(1, len(rows)), 1)
        for r, text in zip(rows, responses):
            res = annotate_item_modal(
                r["vid"], r["proverb"], r["options"], r["language"], model,
                response_text=text,
            )
            res["run_id"] = run_id
            res["latency_ms"] = per_item_ms
            results.append(res)

    out_df = pd.DataFrame(results)
    out_path = os.path.join(output_dir, f"modal_annotation_results_{run_id}.csv")
    out_df.to_csv(out_path, index=False)
    return out_path


if __name__ == "__main__":
    sample = os.path.join(
        "..",
        "data",
        "production",
        "paper_first_outputs_2026-06-22_10-42-02",
        "human_validation_sample_60.csv",
    )
    if not os.path.exists(sample):
        print(f"Sample file not found: {sample}")
        sys.exit(1)
    print("Modal annotator (open-weight, vLLM, one image per model)")
    print(f"Input: {sample}")
    print(f"Modal token set: {_load_env_token() is not None}")
    print(f"Apps ready: {len(_REGISTRY)} | models: {list(_REGISTRY.keys())}")
    if _REGISTRY:
        path = run_modal_annotation(sample)
        print(f"Results: {path}")
    else:
        print("Fix the Modal app build error before running live.")
