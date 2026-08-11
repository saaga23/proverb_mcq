import modal, sys, subprocess, json, time

modal.enable_output()
img = modal.Image.debian_slim()
ap = modal.App("diag_final")


@ap.function(gpu="A100", timeout=1800)
def probe():
    info = {"executable": sys.executable, "path": sys.path}
    # Try installing torch and capture everything.
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", "torch", "--no-cache-dir"],
            capture_output=True, text=True, timeout=900,
        )
        info["pip_returncode"] = r.returncode
        info["pip_stdout_tail"] = r.stdout[-1500:]
        info["pip_stderr_tail"] = r.stderr[-1500:]
    except Exception as e:
        info["pip_exc"] = repr(e)
    try:
        import torch
        info["torch_version"] = torch.__version__
    except Exception as e:
        info["torch_err"] = repr(e)
    return info


t0 = time.time()
with ap.run():
    print(json.dumps(probe.remote(), indent=2, default=str))
print("elapsed %.1fs" % (time.time() - t0))
