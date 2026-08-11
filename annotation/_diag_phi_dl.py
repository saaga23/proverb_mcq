import modal, time

modal.enable_output()

MODEL = "microsoft/Phi-3.5-mini-instruct"
ROOT = "/models"
local = os.path.join if False else "/models/microsoft--Phi-3.5-mini-instruct"

img = (
    modal.Image.debian_slim()
    .pip_install("huggingface_hub", "hf-transfer")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "HF_HOME": "/models/.cache"})
)
img = img.run_commands([
    f"mkdir -p {local}",
    f"python -c \"from huggingface_hub import snapshot_download; print('DL_START'); snapshot_download('{MODEL}', local_dir='{local}'); print('DL_DONE')\"",
])

ap = modal.App("diag_phi_dl")


@ap.function(timeout=1200)
def probe():
    import os
    files = os.listdir(local)
    return f"files={len(files)} sample={files[:3]}"


t0 = time.time()
try:
    with ap.run():
        print("RESULT:", probe.remote(), "elapsed %.1fs" % (time.time() - t0))
except Exception as e:
    print("ERR:", repr(e)[:800])
