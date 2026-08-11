import modal, time, os
from pathlib import Path

modal.enable_output()

# Load HF token the same way the module does.
hf = None
if os.environ.get("HF_TOKEN"):
    hf = os.environ["HF_TOKEN"]
elif Path(".env").exists():
    for line in Path(".env").read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("HF_TOKEN="):
            hf = line.split("=", 1)[1].strip().strip("\"'")
            break
print("HF_TOKEN present:", bool(hf), "| len:", len(hf) if hf else 0)

img = (
    modal.Image.debian_slim()
    .pip_install("torch", "transformers", "accelerate", "pydantic", "huggingface_hub", "hf-transfer")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "HF_HOME": "/models/.cache",
          "HF_TOKEN": hf or "", "HUGGING_FACE_HUB_TOKEN": hf or ""})
)
img = img.run_commands([
    "mkdir -p /models/meta-llama--Llama-3.2-3B-Instruct",
    "python -c \"from huggingface_hub import snapshot_download; snapshot_download('meta-llama/Llama-3.2-3B-Instruct', local_dir='/models/meta-llama--Llama-3.2-3B-Instruct')\"",
])

ap = modal.App("build_probe_llama", image=img)


@ap.function(gpu="A100", timeout=1200)
def probe():
    from transformers import pipeline

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    p = pipeline("text-generation", model="/models/meta-llama--Llama-3.2-3B-Instruct",
                 torch_dtype="auto", device_map="cuda")
    return str(p("Pick A B C or D: the cat sat. A) yes B) no", max_new_tokens=4, do_sample=False)[0]["generated_text"])


t0 = time.time()
try:
    with ap.run():
        print("RESULT:", probe.remote(), "elapsed %.1fs" % (time.time() - t0))
except Exception as e:
    print("ERR:", repr(e)[:1000])
