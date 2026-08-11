import modal, time, os
from pathlib import Path

modal.enable_output()

MODELS = ["Qwen/Qwen2.5-7B-Instruct", "microsoft/Phi-3.5-mini-instruct"]
ROOT = "/models"


def local_dir(m):
    return os.path.join(ROOT, m.replace("/", "--"))


img = (
    modal.Image.debian_slim()
    .pip_install("torch", "transformers", "accelerate", "pydantic", "huggingface_hub", "hf-transfer")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "HF_HOME": os.path.join(ROOT, ".cache")})
)
for m in MODELS:
    img = img.run_commands([
        f"mkdir -p {local_dir(m)}",
        f"python -c \"from huggingface_hub import snapshot_download; snapshot_download('{m}', local_dir='{local_dir(m)}')\"",
    ])

ap = modal.App("build_probe_combined", image=img)


@ap.function(gpu="A100", timeout=1800)
def probe(model):
    from transformers import pipeline

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    p = pipeline("text-generation", model=local_dir(model), torch_dtype="auto", device_map="cuda")
    return str(p("Pick A B C or D: the cat sat. A) yes B) no", max_new_tokens=4, do_sample=False)[0]["generated_text"])


t0 = time.time()
try:
    with ap.run():
        for m in MODELS:
            print("RESULT", m, ":", probe.remote(m), flush=True)
    print("elapsed %.1fs" % (time.time() - t0))
except Exception as e:
    print("ERR:", repr(e)[:1200])
