#!/usr/bin/env python3
"""Convert a versioned Resume IR (YAML) into the editor's resume.json.

The editor (assets/editor/index.html) reads a flat resume.json with:
    { "basics": {...}, "sections": [...], "style": {...} }

This script maps the structured IR (resume_ir_vN.yaml) into that shape so the
micro-adjust editor can be launched right after a resume is generated.

Usage:
    python ir_to_editor_json.py resume_ir_v1.yaml --output <editor_dir>/resume.json

Dependency: PyYAML (pip install pyyaml). If unavailable, falls back to a clear error.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_STYLE = {
    "fontSize": 10,
    "lineHeight": 1.5,
    "sectionGap": 13,
    "itemGap": 8,
    "bulletGap": 3,
    "pagePadding": 15,
    "accent": "#0f766e",
    "template": "modern",
}


def load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore
    except Exception:
        raise SystemExit("需要 PyYAML：pip install pyyaml（或用对应虚拟环境的 pip）")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def join_text(bullet: dict) -> str:
    """Assemble bullet text from IR fields (action/technology/result)."""
    action = (bullet.get("action") or "").strip()
    tech = bullet.get("technology") or []
    result = (bullet.get("result") or "").strip()
    parts = []
    if action:
        parts.append(action)
    if tech:
        parts.append(" / ".join(t for t in tech if t))
    if result:
        parts.append(result)
    return "，".join(p for p in parts if p)


def convert(ir: dict) -> dict:
    cand = ir.get("candidate", {})
    contact = cand.get("contact", {})
    basics = {
        "name": cand.get("name", ""),
        "title": (cand.get("target_roles") or [""])[0],
        "phone": contact.get("phone", ""),
        "email": contact.get("email", ""),
        "location": contact.get("location", ""),
        "photo": cand.get("photo", "") or "",
    }

    sections = []

    edu = ir.get("education") or []
    if edu:
        items = []
        for e in edu:
            heading = " · ".join(x for x in [e.get("school"), e.get("major"), e.get("degree")] if x)
            items.append({
                "heading": heading,
                "subheading": e.get("notes", "") or e.get("gpa", "") or "",
                "date": (e.get("end") or ""),
                "bullets": [],
            })
        sections.append({"id": "education", "title": "教育经历", "visible": True, "items": items})

    exps = ir.get("experiences") or []
    if exps:
        items = []
        for x in exps:
            items.append({
                "heading": f"{x.get('organization','')} · {x.get('role','')}".strip(" ·"),
                "subheading": " ｜ ".join(x.get("tech_stack") or []),
                "date": f"{x.get('start','')} - {x.get('end','')}".strip(" -"),
                "bullets": [{"highlight": b.get("highlight", ""), "text": join_text(b)} for b in (x.get("bullets") or [])],
            })
        sections.append({"id": "experiences", "title": "实习 / 工作经历", "visible": True, "items": items})

    projs = ir.get("projects") or []
    if projs:
        items = []
        for p in projs:
            items.append({
                "heading": f"{p.get('name','')}（{p.get('role','')}）".replace("（）", ""),
                "subheading": " ｜ ".join(p.get("tech_stack") or []),
                "date": f"{p.get('start','')} - {p.get('end','')}".strip(" -"),
                "bullets": [{"highlight": b.get("highlight", ""), "text": join_text(b)} for b in (p.get("bullets") or [])],
            })
        sections.append({"id": "projects", "title": "项目经历", "visible": True, "items": items})

    skills = ir.get("skills") or {}
    if skills:
        label_map = {
            "languages": "编程语言",
            "frameworks": "框架",
            "databases_middleware": "数据与中间件",
            "cloud_engineering": "工程能力",
            "ai_domain": "AI 领域",
        }
        bullets = []
        for k, label in label_map.items():
            vals = skills.get(k) or []
            if vals:
                bullets.append({"highlight": label, "text": "、".join(vals)})
        if bullets:
            sections.append({"id": "skills", "title": "专业技能", "visible": True,
                             "items": [{"heading": "", "subheading": "", "date": "", "bullets": bullets}]})

    return {"basics": basics, "sections": sections, "style": dict(DEFAULT_STYLE)}


def main() -> None:
    ap = argparse.ArgumentParser(description="Convert Resume IR (YAML) to editor resume.json")
    ap.add_argument("ir_file", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    if not args.ir_file.is_file():
        raise SystemExit(f"IR 文件不存在：{args.ir_file}")
    ir = load_yaml(args.ir_file)
    data = convert(ir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成：{args.output}")
    print("启动微调器：python scripts/serve_resume_editor.py <editor_dir> --port 8618")


if __name__ == "__main__":
    main()
