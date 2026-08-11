#!/usr/bin/env python3
"""
Push the Pilot 1 TEST notebook to Kaggle and immediately run all cells.

The Kaggle CLI `kernels push` only saves a new version. The web UI "Run" button
maps to ApiSaveKernelRequest with kernel_execution_type=SAVE_AND_RUN_ALL. This
script does both in one call.
"""
import json
import os
import time
import argparse

from kagglesdk import KaggleClient
from kagglesdk.kernels.types.kernels_api_service import (
    ApiSaveKernelRequest,
    KernelExecutionType,
)


def push_and_run(kernel_slug: str, metadata_path: str, notebook_path: str) -> dict:
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    with open(notebook_path, "r", encoding="utf-8") as f:
        script_body = f.read()

    # Clean notebook outputs so Kaggle starts fresh.
    if meta.get("kernel_type") == "notebook":
        nb = json.loads(script_body)
        if "cells" in nb:
            for cell in nb["cells"]:
                if cell.get("cell_type") == "code" and "outputs" in cell:
                    cell["outputs"] = []
                if isinstance(cell.get("source"), list):
                    cell["source"] = "".join(cell["source"])
        script_body = json.dumps(nb)

    client = KaggleClient()
    req = ApiSaveKernelRequest()
    req.slug = kernel_slug
    req.new_title = meta.get("title")
    req.text = script_body
    req.language = meta.get("language", "python")
    req.kernel_type = meta.get("kernel_type", "notebook")
    req.is_private = meta.get("is_private", True)
    req.enable_gpu = meta.get("enable_gpu", False)
    req.enable_tpu = meta.get("enable_tpu", False)
    req.enable_internet = meta.get("enable_internet", True)
    req.dataset_data_sources = meta.get("dataset_sources", [])
    req.competition_data_sources = meta.get("competition_sources", [])
    req.kernel_data_sources = meta.get("kernel_sources", [])
    req.model_data_sources = meta.get("model_sources", [])
    req.kernel_execution_type = KernelExecutionType.SAVE_AND_RUN_ALL

    resp = client.kernels.kernels_api_client.save_kernel(req)
    return resp


def main():
    parser = argparse.ArgumentParser(description="Push and run a Kaggle kernel.")
    parser.add_argument(
        "--slug",
        default="abrahamsunday123/mcq-pass-shortcut",
        help="Kernel slug",
    )
    parser.add_argument(
        "--metadata",
        default="kaggle_upload_pilot1_test/kernel-metadata.json",
        help="Path to kernel-metadata.json",
    )
    parser.add_argument(
        "--notebook",
        default="openrouter_pilot_distractor_generation_test_nano_opus.ipynb",
        help="Path to notebook (.ipynb)",
    )
    args = parser.parse_args()

    print(f"Pushing and running {args.slug} ...")
    resp = push_and_run(args.slug, args.metadata, args.notebook)
    print(resp)
    print("Run triggered. Poll status with:")
    print(f'  python -m kaggle kernels status "{args.slug}"')


if __name__ == "__main__":
    main()
