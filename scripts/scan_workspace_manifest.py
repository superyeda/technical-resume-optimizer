#!/usr/bin/env python3
"""Build a read-only, privacy-aware workspace manifest for resume evidence collection."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

EXCLUDED_DIRS = {
    ".git", ".idea", ".vscode", "node_modules", "vendor", "dist", "build",
    "target", "coverage", ".next", ".cache", "__pycache__", ".venv", "venv",
}
SENSITIVE_NAMES = {
    ".env", ".env.local", ".env.production", "id_rsa", "id_ed25519",
    "credentials.json", "secrets.json",
}
ALLOWED_SUFFIXES = {
    ".md", ".txt", ".pdf", ".docx", ".png", ".jpg", ".jpeg", ".webp",
    ".rst", ".adoc", ".tex", ".yaml", ".yml", ".json",
}


def sha256_prefix(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        digest.update(handle.read(1024 * 1024))
    return digest.hexdigest()[:16]


def classify(path: Path) -> str:
    name = path.name.lower()
    if "resume" in name or "简历" in name:
        return "resume"
    if any(token in name for token in ("readme", "设计", "design", "复盘", "report", "论文", "paper", "award", "获奖")):
        return "high_priority_evidence"
    if path.suffix.lower() in {".md", ".txt", ".pdf", ".docx"}:
        return "document"
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
        return "image"
    return "metadata"


def build_manifest(root: Path) -> dict:
    files = []
    skipped = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            skipped.append({"path": str(relative), "reason": "excluded_directory"})
            continue
        if path.name.lower() in SENSITIVE_NAMES or path.suffix.lower() in {".pem", ".key", ".pfx"}:
            skipped.append({"path": str(relative), "reason": "sensitive_file"})
            continue
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            continue
        stat = path.stat()
        files.append({
            "path": str(relative).replace("\\", "/"),
            "type": classify(path),
            "suffix": path.suffix.lower(),
            "size_bytes": stat.st_size,
            "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "sha256_prefix": sha256_prefix(path),
        })
    return {
        "schema_version": 1,
        "workspace": str(root.resolve()),
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "files": sorted(files, key=lambda item: (item["type"], item["path"])),
        "skipped": skipped,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a workspace manifest for resume evidence extraction.")
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.workspace.resolve()
    if not root.is_dir():
        raise SystemExit(f"Workspace does not exist or is not a directory: {root}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(build_manifest(root), ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
