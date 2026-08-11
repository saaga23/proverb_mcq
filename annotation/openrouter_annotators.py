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

Respond with ONLY a single letter (A, B, C, or D). Do not include any other text."""

DEFAULT_OPENROUTER_MODELS = [
    "openai/gpt-4o-mini",
    "anthropic/claude-3-haiku",
    "google/gemini-2.5-flash",
]

OUTPUT_DIR = "annotation/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
LOG_PATH = os.path.join(OUTPUT_DIR, "openrouter_annotator_log.jsonl")


def _redact(text: str) -> str:
    if not isinstance(text, str):
        return text
    return re.sub(r"(sk-|api[_-]?key|token|secret)\s*[:=]\s*\S+", r"\1=***REDACTED***", text, flags=re.IGNORECASE)


def _load_api_key() -> Optional[str]:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        env_path = Path(".env")
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("OPENROUTER_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip("\"'")
                    break
    return key


def _estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    pricing = {
        "openai/gpt-4o": (2.5, 10.0),
        "openai/gpt-4o-mini": (0.15, 0.60),
        "anthropic/claude-haiku-3": (0.25, 1.25),
        "anthropic/claude-3-haiku": (0.25, 1.25),
        "anthropic/claude-3-5-haiku": (0.25, 1.25),
        "google/gemini-2.5-flash": (0.15, 0.60),
        "google/gemini-2.5-pro": (1.25, 10.0),
        "qwen/qwen3.7-max": (1.25, 3.75),
        "qwen/qwen3.5-397b-a17b": (0.39, 0.90),
        "deepseek/deepseek-v3.2": (0.2288, 0.3432),
        "mistralai/mistral-small-3.2-24b-instruct": (0.075, 0.20),
        "meta-llama/llama-3.3-70b-instruct": (0.10, 0.32),
        "google/gemma-3-27b-it": (0.08, 0.16),
        "google/gemma-4-31b-it": (0.12, 0.36),
    }
    inp, out = pricing.get(model, (2.0, 8.0))
    return (prompt_tokens * inp + completion_tokens * out) / 1_000_000


def _extract_answer(text: str) -> Optional[str]:
    if not text:
        return None
    text = str(text).strip()
    matches = re.findall(r'\b([ABCD])\b', text, re.IGNORECASE)
    if matches:
        return matches[-1].upper()
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


def get_openrouter_annotator_models() -> List[str]:
    api_key = _load_api_key()
    if not api_key:
        return DEFAULT_OPENROUTER_MODELS
    try:
        import requests
        resp = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            available = {m["id"] for m in data.get("data", [])}
            return [m for m in DEFAULT_OPENROUTER_MODELS if m in available] or DEFAULT_OPENROUTER_MODELS
    except Exception:
        pass
    return DEFAULT_OPENROUTER_MODELS


def annotate_item_openrouter(
    validation_id: str,
    proverb: str,
    options: Dict[str, str],
    language: str,
    model: str,
    temperature: float = 0.0,
    max_tokens: int = 10,
    retries: int = 3,
    base_delay: float = 1.0,
) -> Dict:
    try:
        import requests
    except ImportError:
        return {
            "validation_id": validation_id,
            "language": language,
            "model": model,
            "answer": None,
            "confidence": None,
            "latency_ms": None,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "cost_usd": 0.0,
            "finish_reason": "error",
            "errors": "requests package not installed",
        }

    api_key = _load_api_key()
    if not api_key:
        return {
            "validation_id": validation_id,
            "language": language,
            "model": model,
            "answer": None,
            "confidence": None,
            "latency_ms": None,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "cost_usd": 0.0,
            "finish_reason": "error",
            "errors": "OPENROUTER_API_KEY not set",
        }

    prompt = ANNOTATION_PROMPT_TEMPLATE.format(
        proverb=proverb,
        option_a=options.get("A", ""),
        option_b=options.get("B", ""),
        option_c=options.get("C", ""),
        option_d=options.get("D", ""),
    )

    record = {
        "run_id": os.environ.get("ANNOTATION_RUN_ID", "openrouter_manual"),
        "validation_id": validation_id,
        "language": language,
        "model": model,
        "prompt": prompt,
        "response": "",
        "finish_reason": "attempting",
        "errors": "",
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    for attempt in range(1, retries + 1):
        try:
            t0 = time.time()
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            latency = (time.time() - t0) * 1000
            if resp.status_code == 429 and attempt < retries:
                time.sleep(base_delay * (2 ** (attempt - 1)))
                continue
            resp.raise_for_status()
            data = resp.json()
            text = ""
            if "choices" in data and data["choices"]:
                text = data["choices"][0].get("message", {}).get("content", "")
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            cost = _estimate_cost(model, prompt_tokens, completion_tokens)
            answer = _extract_answer(text)
            record.update({
                "response": text,
                "finish_reason": "ok" if answer else "parse_failed",
                "errors": "" if answer else f"Failed to extract A/B/C/D from: {text!r}",
            })
            return {
                "validation_id": validation_id,
                "language": language,
                "model": model,
                "answer": answer,
                "confidence": None,
                "latency_ms": round(latency, 1),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cost_usd": round(cost, 6),
                "finish_reason": record["finish_reason"],
                "errors": record["errors"],
            }
        except Exception as exc:
            record["errors"] = str(exc)
            record["finish_reason"] = "exception"
            if attempt == retries:
                return {
                    "validation_id": validation_id,
                    "language": language,
                    "model": model,
                    "answer": None,
                    "confidence": None,
                    "latency_ms": None,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "cost_usd": 0.0,
                    "finish_reason": "exception",
                    "errors": str(exc),
                }
        finally:
            _log(record)
    return {
        "validation_id": validation_id,
        "language": language,
        "model": model,
        "answer": None,
        "confidence": None,
        "latency_ms": None,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "cost_usd": 0.0,
        "finish_reason": "exhausted_retries",
        "errors": "All retries failed",
    }


def run_openrouter_annotation(
    csv_path: str,
    output_dir: str = OUTPUT_DIR,
    models: Optional[List[str]] = None,
    max_items: Optional[int] = None,
    cost_cap: float = 5.0,
) -> Tuple[str, float]:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(csv_path)
    if max_items:
        df = df.head(max_items)
    models = models or get_openrouter_annotator_models()

    run_id = f"openrouter_annotator_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    os.environ["ANNOTATION_RUN_ID"] = run_id
    results: List[Dict] = []
    total_cost = 0.0

    for _, row in df.iterrows():
        proverb = str(row.get("proverb", ""))
        options = {k: str(row.get(f"option_{k}", row.get(k, ""))) for k in ("A", "B", "C", "D")}
        language = str(row.get("language", ""))
        vid = str(row.get("validation_id", row.get("mcq_id", "")))

        for model in models:
            if total_cost >= cost_cap:
                break
            res = annotate_item_openrouter(vid, proverb, options, language, model)
            res["run_id"] = run_id
            total_cost += res.get("cost_usd", 0.0)
            results.append(res)

    out_df = pd.DataFrame(results)
    out_path = os.path.join(output_dir, f"openrouter_annotation_results_{run_id}.csv")
    out_df.to_csv(out_path, index=False)
    return out_path, total_cost


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
    print("OpenRouter annotator smoke test")
    print(f"Input: {sample}")
    print(f"Models: {get_openrouter_annotator_models()}")
    if _load_api_key():
        path, cost = run_openrouter_annotation(sample, max_items=5)
        print(f"Results: {path}")
        print(f"Cost: ${cost:.4f}")
    else:
        print("Set OPENROUTER_API_KEY to run live. Generating mock results for 5 items.")
        df = pd.read_csv(sample).head(5)
        mock = []
        for _, r in df.iterrows():
            mock.append({
                "run_id": "openrouter_mock",
                "validation_id": r.get("validation_id", ""),
                "language": r.get("language", ""),
                "model": "mock/GPT-4o",
                "answer": "A",
                "confidence": None,
                "latency_ms": 567.8,
                "prompt_tokens": 64,
                "completion_tokens": 1,
                "cost_usd": 0.0012,
                "finish_reason": "ok",
                "errors": "",
            })
        pd.DataFrame(mock).to_csv(os.path.join(OUTPUT_DIR, "openrouter_annotation_mock.csv"), index=False)
        print("Mock results saved.")
