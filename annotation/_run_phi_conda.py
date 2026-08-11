import modal, os, time, json, subprocess
from pathlib import Path
from datetime import datetime, timezone

modal.enable_output()

MODEL = "microsoft/Phi-3.5-mini-instruct"
ROOT = "/models"
local = os.path.join(ROOT, MODEL.replace("/", "--"))
CONDA = "/opt/conda/bin/python"
SAMPLE = Path(__file__).resolve().parent.parent / "paper_first_outputs_2026-06-22_10-42-02" / "human_validation_sample_60.csv"

# Base image already has torch in /opt/conda. Install the lighter deps into the
# SAME conda python via build-time run_command. The Modal function then shells
# inference out to /opt/conda/bin/python (which has torch).
INFER = r'''
import os, json, re, sys
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import snapshot_download
MODEL = "microsoft/Phi-3.5-mini-instruct"
local = "/models/microsoft--Phi-3.5-mini-instruct"
if not os.path.isdir(local) or not any(os.scandir(local)):
    os.makedirs(local, exist_ok=True); snapshot_download(MODEL, local_dir=local)
os.environ["HF_HUB_OFFLINE"]="1"; os.environ["TRANSFORMERS_OFFLINE"]="1"
tok = AutoTokenizer.from_pretrained(local)
mdl = AutoModelForCausalLM.from_pretrained(local, torch_dtype="auto", device_map="cuda")
import torch
dev = next(mdl.parameters()).device
rows = json.load(open("/tmp/prompts.json"))
tmpl = ("You are an expert annotator for proverb understanding.\n"
        "Given the following proverb and four candidate meanings, select the ONE correct meaning.\n\n"
        "Proverb: {proverb}\nOptions:\nA) {A}\nB) {B}\nC) {C}\nD) {D}\n\n"
        "Respond with ONLY a single letter (A, B, C, or D). Do not include any other text.")
out=[]
for r in rows:
    p=tmpl.format(proverb=r["proverb"],A=r["A"],B=r["B"],C=r["C"],D=r["D"])
    ids=tok.apply_chat_template([{"role":"user","content":p}],tokenize=True,add_generation_prompt=True,return_tensors="pt").to(dev)
    g=mdl.generate(ids,max_new_tokens=16,do_sample=False,temperature=1.0,pad_token_id=tok.eos_token_id)
    txt=tok.decode(g[0][ids.shape[1]:],skip_special_tokens=True).strip()
    m=re.search(r"\b([ABCD])\b",txt)
    out.append({"validation_id":r["vid"],"language":r["lang"],"answer":m.group(1) if m else None,"raw":txt})
json.dump(out, open("/tmp/results.json","w"), ensure_ascii=False)
'''

img = (
    modal.Image.from_registry("pytorch/pytorch:2.3.1-cuda121-cudnn8-runtime")
    .run_commands([
        "pip install -q transformers accelerate huggingface_hub hf-transfer",
        f"python -c \"import torch; print('base_torch', torch.__version__, torch.__file__)\"",
    ])
)
ap = modal.App("phi_conda_run")


@ap.function(gpu="A100", timeout=2400)
def annotate(rows):
    import subprocess as _sp
    Path("/tmp/prompts.json").write_text(json.dumps(rows))
    Path("/tmp/infer.py").write_text(INFER)
    # Discover the interpreter that actually has torch (Modal's function python
    # lacks it; the base image's python does, but its path varies per image).
    candidates = ["/usr/bin/python3", "/usr/local/bin/python3", "/opt/conda/bin/python",
                  "python3", "python"]
    torch_py = None
    for c in candidates:
        try:
            r = _sp.run([c, "-c", "import torch, transformers; print('OK')"],
                        capture_output=True, text=True, timeout=120)
            if r.returncode == 0:
                torch_py = c
                break
        except Exception:
            continue
    if not torch_py:
        return {"error": "no torch interpreter found", "candidates": candidates}
    r = _sp.run([torch_py, "/tmp/infer.py"], capture_output=True, text=True, timeout=2000)
    if r.returncode != 0:
        return {"error": r.stderr[-2000:], "stdout": r.stdout[-1000:], "torch_py": torch_py}
    return json.loads(Path("/tmp/results.json").read_text())


def main():
    import pandas as pd
    df = pd.read_csv(SAMPLE).head(5)
    rows = [{"vid": str(r["validation_id"]), "lang": str(r["language"]),
             "proverb": str(r["proverb"]),
             "A": str(r.get("option_A","")), "B": str(r.get("option_B","")),
             "C": str(r.get("option_C","")), "D": str(r.get("option_D",""))} for _, r in df.iterrows()]
    t0 = time.time()
    with ap.run():
        res = annotate.remote(rows)
    print("ELAPSED %.1fs" % (time.time() - t0))
    print(json.dumps(res, ensure_ascii=False, indent=2))
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    Path("outputs").mkdir(exist_ok=True)
    pd.DataFrame(res if isinstance(res, list) else [res]).to_csv(f"outputs/phi_conda_{ts}.csv", index=False)
    print("WROTE outputs/phi_conda_%s.csv" % ts)


if __name__ == "__main__":
    main()
