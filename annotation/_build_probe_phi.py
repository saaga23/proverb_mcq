import modal, time, os

modal.enable_output()

MODEL = "microsoft/Phi-3.5-mini-instruct"
ROOT = "/models"
local = os.path.join(ROOT, MODEL.replace("/", "--"))

img = (
    modal.Image.debian_slim()
    .pip_install("torch", "transformers", "accelerate", "pydantic", "huggingface_hub", "hf-transfer")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "HF_HOME": os.path.join(ROOT, ".cache")})
)
img = img.run_commands([
    f"mkdir -p {local}",
    f"python -c \"from huggingface_hub import snapshot_download; snapshot_download('{MODEL}', local_dir='{local}')\"",
])

ap = modal.App("build_probe_phi", image=img)

PROMPT = (
    "You are an expert annotator for proverb understanding.\n"
    "Given the following proverb and four candidate meanings, select the ONE correct meaning.\n\n"
    "Proverb: A stitch in time saves nine.\n"
    "Options:\nA) Fixing problems early prevents bigger ones later\n"
    "B) Sewing is a valuable life skill\nC) Time passes quickly\nD) Nine is a lucky number\n\n"
    "Respond with ONLY a single letter (A, B, C, or D). Do not include any other text."
)


@ap.function(gpu="A100", timeout=1800)
def probe():
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    tok = AutoTokenizer.from_pretrained(local)
    mdl = AutoModelForCausalLM.from_pretrained(local, torch_dtype="auto", device_map="cuda")
    device = next(mdl.parameters()).device
    input_ids = tok.apply_chat_template(
        [{"role": "user", "content": PROMPT}],
        tokenize=True, add_generation_prompt=True, return_tensors="pt",
    ).to(device)
    out = mdl.generate(input_ids, max_new_tokens=16, do_sample=False, temperature=1.0,
                       pad_token_id=tok.eos_token_id)
    return tok.decode(out[0][input_ids.shape[1]:], skip_special_tokens=True).strip()


t0 = time.time()
try:
    with ap.run():
        print("RESULT:", repr(probe.remote()), "elapsed %.1fs" % (time.time() - t0))
except Exception as e:
    print("ERR:", repr(e)[:1200])
