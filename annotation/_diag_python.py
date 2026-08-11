import modal, sys, time

modal.enable_output()

img = (
    modal.Image.debian_slim()
    .pip_install("torch", "transformers")
    .run_commands([
        "python -c \"import sys, torch; print('BUILD_EXEC', sys.executable); print('BUILD_TORCH', torch.__file__); print('BUILD_VER', torch.__version__)\"",
    ])
)
ap = modal.App("diag_python")


@ap.function(gpu="A100", timeout=1200)
def probe():
    import sys
    out = {"RUNTIME_EXEC": sys.executable}
    try:
        import torch
        out["RUNTIME_TORCH"] = torch.__file__
        out["RUNTIME_VER"] = torch.__version__
    except Exception as e:
        out["RUNTIME_ERR"] = repr(e)
    return out


t0 = time.time()
try:
    with ap.run():
        print("RESULT:", probe.remote(), "elapsed %.1fs" % (time.time() - t0))
except Exception as e:
    print("ERR:", repr(e)[:500])
