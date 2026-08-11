import modal, time, traceback

modal.enable_output()

img = (
    modal.Image.from_registry(
        "pytorch/pytorch:2.3.1-cuda121-cudnn8-runtime",
        add_python="3.11",
    )
    .pip_install("transformers", "accelerate", "huggingface_hub", "hf-transfer")
    .run_commands(["python -c \"import torch, transformers; print('ok', torch.__version__, transformers.__version__)\""])
)
ap = modal.App("diag_torch_base")


@ap.function(gpu="A100", timeout=1200)
def probe():
    return "ran"


t0 = time.time()
try:
    with ap.run():
        print("RESULT:", probe.remote(), "elapsed %.1fs" % (time.time() - t0))
except Exception as e:
    print("ERR_TOP:", repr(e)[:500])
    traceback.print_exc()
