import modal, os, time, re, json, sys, subprocess, importlib
from pathlib import Path
from datetime import datetime, timezone

modal.enable_output()

MODEL = "microsoft/Phi-3.5-mini-instruct"
ROOT = "/models"
local = os.path.join(ROOT, MODEL.replace("/", "--"))
SAMPLE = Path(__file__).resolve().parent.parent / "paper_first_outputs_2026-06-22_10-42-02" / "human_validation_sample_60.csv"

# Minimal image; all heavy packages are installed at runtime in the SAME
# interpreter Modal's function actually runs (/usr/local/bin/python), which is
# where pip_install was NOT landing.
img = modal.Image.debian_slim()
ap = modal.App("phi_runtime_install")


def _ensure(pkg, extras=None):
    try:
        importlib.import_module(pkg)
    except ImportError:
        spec = pkg if not extras else f"{pkg}{extras}"
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", spec], check=True)


@ap.function(gpu="A100", timeout=2400)
def annotate(rows):
    _ensure("torch")
    _ensure("transformers")
    _ensure("accelerate")
    _ensure("huggingface_hub")
    _ensure("hf_transfer")

    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from huggingface_hub import snapshot_download

    if not os.path.isdir(local) or not any(os.scandir(local)):
        os.makedirs(local, exist_ok=True)
        snapshot_download(MODEL, local_dir=local)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    tok = AutoTokenizer.from_pretrained(local)
    mdl = AutoModelForCausalLM.from_pretrained(local, torch_dtype="auto", device_map="cuda")
    device = next(mdl.parameters()).device

    tmpl = (
        "You are an expert annotator for proverb understanding.\n"
        "Given the following proverb and four candidate meanings, select the ONE correct meaning.\n\n"
        "Proverb: {proverb}\nOptions:\nA) {A}\nB) {B}\nC) {C}\nD) {D}\n\n"
        "Respond with ONLY a single letter (A, B, C, or D). Do not include any other text."
    )
    out = []
    for r in rows:
        p = tmpl.format(proverb=r["proverb"], A=r["A"], B=r["B"], C=r["C"], D=r["D"])
        ids = tok.apply_chat_template([{"role": "user", "content": p}], tokenize=True,
                                      add_generation_prompt=True, return_tensors="pt").to(device)
        gen = mdl.generate(ids, max_new_tokens=16, do_sample=False, temperature=1.0,
                           pad_token_id=tok.eos_token_id)
        txt = tok.decode(gen[0][ids.shape[1]:], skip_special_tokens=True).strip()
        m = re.search(r"\b([ABCD])\b", txt)
        out.append({"validation_id": r["vid"], "language": r["lang"], "answer": m.group(1) if m else None, "raw": txt})
    return out


def main():
    import pandas as pd
    df = pd.read_csv(SAMPLE).head(5)
    rows = [{"vid": str(r["validation_id"]), "lang": str(r["language"]),
             "proverb": str(r["proverb"]),
             "A": str(r.get("option_A", "")), "B": str(r.get("option_B", "")),
             "C": str(r.get("option_C", "")), "D": str(r.get("option_D", ""))} for _, r in df.iterrows()]
    t0 = time.time()
    with ap.run():
        res = annotate.remote(rows)
    print("ELAPSED %.1fs" % (time.time() - t0))
    print(json.dumps(res, ensure_ascii=False, indent=2))
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    Path("outputs").mkdir(exist_ok=True)
    pd.DataFrame(res).to_csv(f"outputs/phi_standalone_{ts}.csv", index=False)
    print("WROTE outputs/phi_standalone_%s.csv" % ts)


if __name__ == "__main__":
    main()
