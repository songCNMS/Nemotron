#!/usr/bin/env python3

"""Import the local Qwen3 4B HF checkpoint into Megatron-Bridge format."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch
from megatron.bridge import AutoBridge


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hf-path", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    print(f"IMPORT_HF={args.hf_path}", flush=True)
    print(f"IMPORT_OUT={args.output_dir}", flush=True)
    AutoBridge.import_ckpt(
        args.hf_path,
        args.output_dir,
        torch_dtype=torch.bfloat16,
        device_map="cpu",
        trust_remote_code=True,
    )
    print("IMPORT_DONE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
