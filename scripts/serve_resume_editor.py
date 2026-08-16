#!/usr/bin/env python3
"""Serve the resume editor as a local HTTP server.

Usage:
    python serve_resume_editor.py [editor_dir] [--port 8618] [--output DIR]

- editor_dir : directory containing index.html + demo-resume.json
               (defaults to the assets/editor folder next to this script)
- --port     : local port (default 8618)
- --output   : directory to write the adjusted resume back to on POST /save
               (defaults to a "micro-adjusted" folder next to editor_dir)

Routes:
    GET  /              editor page
    GET  /resume.json   resume data (the editor fetches demo-resume.json)
    POST /save          write the adjusted resume.json + generated HTML back
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_EDITOR_DIR = SCRIPT_DIR.parent / "assets" / "editor"


def esc(v):
    return (v or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def md_bold(v):
    """Convert markdown **bold** markers in inline text to <strong>."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(v))


def render_items_html(items: list, kind: str) -> str:
    """Render section items into the template's item HTML fragments.
    kind: experience | project | skill | education
    """
    out = []
    if kind == "skill":
        for it in items:
            for bl in it.get("bullets", []):
                hl = esc(bl.get("highlight", ""))
                txt = md_bold(bl.get("text", ""))
                out.append(f"<p class='skill'><span class='label'>{hl}</span>{txt}</p>")
        return "\n".join(out)

    for it in items:
        heading = esc(it.get("heading", ""))
        date = esc(it.get("date", ""))
        sub = esc(it.get("subheading", ""))
        parts = []
        if heading or date:
            parts.append(f"<div class='item-head'><span>{heading}</span>")
            if date:
                parts.append(f"<span class='date'>{date}</span>")
            parts.append("</div>")
        if sub:
            parts.append(f"<div class='stack'>{sub}</div>")
        bls = it.get("bullets") or []
        if bls:
            parts.append("<ul>")
            for bl in bls:
                hl = esc(bl.get("highlight", ""))
                txt = md_bold(bl.get("text", ""))
                if hl:
                    parts.append(f"<li><strong>{hl}</strong>：{txt}</li>")
                else:
                    parts.append(f"<li>{txt}</li>")
            parts.append("</ul>")
        parts.append("</div>")
        out.append("".join(parts))
    return "\n".join(out)


def build_html(resume: dict) -> str:
    """Render a final resume HTML by filling the official templates.

    Unlike the earlier inline-CSS version, this reads the same template files
    (assets/html-*-template.html) used by the skill's normal generation, so the
    micro-adjusted output is visually identical to the delivered static HTML.
    """
    b = resume.get("basics", {})
    s = resume.get("style", {})
    is_ats = s.get("template") == "ats"
    tpl_name = "html-ats-single-column-template.html" if is_ats else "html-modern-template.html"
    tpl_path = SCRIPT_DIR.parent / "assets" / tpl_name
    if not tpl_path.is_file():
        raise RuntimeError(f"模板不存在：{tpl_path}")
    html = tpl_path.read_text(encoding="utf-8")

    # 1) 按 section id 映射到模板栏目
    sections = {sec.get("id"): sec for sec in resume.get("sections", [])}
    skill_html = render_items_html((sections.get("skills") or {}).get("items", []), "skill")
    proj_html = render_items_html((sections.get("projects") or {}).get("items", []), "project")
    exp_html = render_items_html((sections.get("experiences") or {}).get("items", []), "experience")
    edu_html = render_items_html((sections.get("education") or {}).get("items", []), "education")
    summary_html = md_bold((sections.get("summary") or {}).get("text", ""))

    photo = b.get("photo") or ""
    photo_html = f"<img class='photo-img' src='{photo}' alt=''>" if photo else ""

    repl = {
        "{{name}}": esc(b.get("name", "")),
        "{{target_role}}": esc(b.get("title", "")),
        "{{phone}}": esc(b.get("phone", "")),
        "{{email}}": esc(b.get("email", "")),
        "{{location}}": esc(b.get("location", "")),
        "{{photo_html}}": photo_html,
        "{{summary}}": summary_html,
        "{{experience_items}}": exp_html,
        "{{project_items}}": proj_html,
        "{{skill_items}}": skill_html,
        "{{education_items}}": edu_html,
    }
    for k, v in repl.items():
        html = html.replace(k, v)

    # 2) 注入微调样式参数（字号/行高/间距/主题色/页边距）
    accent = s.get("accent", "#1d4ed8" if is_ats else "#0f766e")
    fs = s.get("fontSize", 10)
    lh = s.get("lineHeight", 1.5)
    sec_gap = s.get("sectionGap", 13)
    item_gap = s.get("itemGap", 8)
    bl_gap = s.get("bulletGap", 3)
    pad = s.get("pagePadding", 15)
    style_override = (
        f"<style>"
        f":root{{--accent:{accent};--teal:{accent};}}"
        f"body{{font:{fs}pt/{lh} \"Microsoft YaHei\",\"PingFang SC\",Arial,sans-serif;}}"
        f"h2{{margin:{sec_gap}pt 0 6pt;}}"
        f".item{{margin:{item_gap}pt 0;}}"
        f"li{{margin:{bl_gap}pt 0;}}"
        f"@page{{size:A4;margin:{pad}mm;}}"
        f"</style>"
    )
    html = html.replace("</head>", style_override + "</head>")
    return html


class Handler(BaseHTTPRequestHandler):
    editor_dir: Path = DEFAULT_EDITOR_DIR
    output_dir: Path = None
    data_file: Path = None  # explicit resume.json path

    def log_message(self, *args):
        sys.stderr.write("[editor] %s\n" % (args[0] % args[1:]))

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _resume_file(self) -> Path:
        if self.data_file and self.data_file.is_file():
            return self.data_file
        return self.editor_dir / "resume.json"

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            fp = self.editor_dir / "index.html"
            if fp.is_file():
                self._send(200, fp.read_bytes())
                return
            self._send(404, "editor index.html not found")
            return
        if path in ("/resume.json", "/demo-resume.json"):
            fp = self._resume_file()
            if fp.is_file():
                self._send(200, fp.read_bytes(), "application/json; charset=utf-8")
                return
            self._send(404, "resume.json not found")
            return
        # static assets under editor_dir
        rel = path.lstrip("/")
        fp = (self.editor_dir / rel).resolve()
        if str(fp).startswith(str(self.editor_dir.resolve())) and fp.is_file():
            self._send(200, fp.read_bytes())
            return
        self._send(404, "not found")

    def do_POST(self):
        if self.path.split("?")[0] != "/save":
            self._send(404, "not found")
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw)
        except Exception as e:
            self._send(400, json.dumps({"ok": False, "error": str(e)}), "application/json")
            return
        out_dir = self.output_dir or (self.editor_dir.parent / "micro-adjusted")
        out_dir.mkdir(parents=True, exist_ok=True)
        name = (data.get("basics", {}).get("name") or "resume")
        (out_dir / f"{name}-微调版.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        (out_dir / f"{name}-微调版.html").write_text(build_html(data), encoding="utf-8")
        self._send(200, json.dumps({"ok": True, "dir": str(out_dir)}), "application/json")


def main():
    ap = argparse.ArgumentParser(description="Serve the resume editor locally.")
    ap.add_argument("editor_dir", nargs="?", default=str(DEFAULT_EDITOR_DIR),
                    help="Directory containing the editor UI (index.html). Defaults to the skill's assets/editor.")
    ap.add_argument("--data", default=None,
                    help="Path to resume.json to edit. If omitted, uses <editor_dir>/resume.json, else demo-resume.json.")
    ap.add_argument("--port", type=int, default=8618)
    ap.add_argument("--output", default=None, help="Directory to write adjusted files on POST /save.")
    args = ap.parse_args()

    Handler.editor_dir = Path(args.editor_dir).resolve()
    if args.data:
        Handler.data_file = Path(args.data).resolve()
    if args.output:
        Handler.output_dir = Path(args.output).resolve()

    # Fallback: if no --data and no resume.json in editor_dir, use demo-resume.json
    default_data = Handler.editor_dir / "resume.json"
    if not Handler.data_file and not default_data.is_file():
        demo = Handler.editor_dir / "demo-resume.json"
        if demo.is_file():
            Handler.data_file = demo

    host = "127.0.0.1"
    server = ThreadingHTTPServer((host, args.port), Handler)
    url = f"http://{host}:{args.port}"
    print(f"简历微调器已启动：{url}")
    print(f"编辑器目录：{Handler.editor_dir}")
    print(f"数据文件：{Handler.data_file or default_data}")
    print(f"写回目录：{Handler.output_dir or (Handler.editor_dir.parent / 'micro-adjusted')}")
    print("按 Ctrl+C 停止服务")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")


if __name__ == "__main__":
    main()
