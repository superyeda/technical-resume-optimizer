#!/usr/bin/env python3
"""Validate required resume delivery artifacts without modifying content."""

from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_SUFFIXES = (".md", ".html")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a technical-resume-optimizer delivery directory.")
    parser.add_argument("delivery_directory", type=Path)
    parser.add_argument("--incremental", action="store_true")
    args = parser.parse_args()
    directory = args.delivery_directory
    if not directory.is_dir():
        raise SystemExit(f"Delivery directory does not exist: {directory}")

    names = [path.name.lower() for path in directory.iterdir() if path.is_file()]
    errors = []
    for suffix in REQUIRED_SUFFIXES:
        if not any(name.endswith(suffix) for name in names):
            errors.append(f"Missing a required {suffix} delivery artifact")
    if not any("评估报告" in name or "assessment" in name for name in names):
        errors.append("Missing assessment report")
    if not any("ats" in name and name.endswith(".html") for name in names):
        errors.append("Missing ATS HTML resume")
    if not any(("现代" in name or "modern" in name) and name.endswith(".html") for name in names):
        errors.append("Missing modern HTML resume")
    if not any("resume_ir_" in name and name.endswith((".yaml", ".yml")) for name in names):
        errors.append("Missing versioned Resume IR")
    if not any("source_manifest_" in name and name.endswith(".json") for name in names):
        errors.append("Missing source manifest")
    if args.incremental and not any("增量变更报告" in name or "incremental" in name for name in names):
        errors.append("Missing incremental change report")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("PASS: Required delivery artifacts are present.")


if __name__ == "__main__":
    main()
