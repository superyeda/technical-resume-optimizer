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
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_EDITOR_DIR = SCRIPT_DIR.parent / "assets" / "editor"


def build_html(resume: dict) -> str:
    """Render a final resume HTML from the structured resume JSON."""
    b = resume.get("basics", {})
    s = resume.get("style", {})
    accent = s.get("accent", "#0f766e")
    is_ats = s.get("template") == "ats"

    def esc(v):
        return (v or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    lines = []
    lines.append("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>")
    lines.append(f"<title>{esc(b.get('name',''))} - 简历</title>")
    lines.append("<style>")
    lines.append(f".resume{{color:#1f2937;font-size:{s.get('fontSize',10)}pt;line-height:{s.get('lineHeight',1.5)}}}")
    if is_ats:
        lines.append(".resume header{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;border-bottom:2px solid #111827;padding-bottom:8px;margin-bottom:4px}")
        lines.append(".resume .head-main{flex:1;min-width:0}")
        lines.append(".resume .name{font-size:20pt;color:#0f172a;margin:0}")
        lines.append(".resume .subtitle{color:#111827;font-weight:600;margin:2px 0 0}")
        lines.append(".resume .contact{color:#4b5563;font-size:9.5pt;margin-top:6px;display:flex;flex-wrap:wrap;gap:4px 12px}")
        lines.append(".resume .photo{width:76px;height:100px;object-fit:cover;border-radius:2px;display:block;flex-shrink:0}")
        lines.append(".resume h2{font-size:12.5pt;color:#111827;border-bottom:1px solid #cbd5e1;padding-bottom:2px;margin:13px 0 6px}")
        lines.append(".resume .date{color:#4b5563;white-space:nowrap}")
    else:
        lines.append(f".resume header{{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;border-bottom:3px solid {accent};padding-bottom:8px}}")
        lines.append(".resume .head-left{flex:1;min-width:0}")
        lines.append(".resume .name{font-size:23pt;color:#0f172a;margin:0}")
        lines.append(f".resume .subtitle{{color:{accent};font-weight:700;margin:4px 0 0}}")
        lines.append(".resume .contact-inline{color:#64748b;font-size:9pt;margin-top:8px;display:flex;flex-wrap:wrap;gap:4px 12px}")
        lines.append(".resume .photo{width:92px;height:120px;object-fit:cover;border-radius:4px;display:block;flex-shrink:0}")
        lines.append(".resume h2{font-size:12.5pt;color:#155e75;margin:13px 0 6px}")
        lines.append(f".resume .date{{color:{accent};white-space:nowrap}}")
    lines.append(".resume .item{margin-bottom:8px}.resume .item-head{display:flex;justify-content:space-between;font-weight:700}")
    lines.append(".resume .stack{color:#64748b;font-size:9pt}")
    lines.append(".resume ul{margin:4px 0 0;padding-left:16px}.resume li{margin:3px 0}")
    lines.append(f"@page{{size:A4;margin:{s.get('pagePadding',15)}mm}}")
    lines.append("</style></head><body>")

    has_photo = b.get("photo")
    lines.append("<div class='resume'>")
    if is_ats:
        lines.append("<header>")
        lines.append("<div class='head-main'>")
        lines.append(f"<h1 class='name'>{esc(b.get('name'))}</h1><p class='subtitle'>{esc(b.get('title'))}</p>")
        lines.append(f"<div class='contact'>{esc(b.get('phone'))} ｜ {esc(b.get('email'))} ｜ {esc(b.get('location'))}</div>")
        lines.append("</div>")
        if has_photo:
            lines.append(f"<img class='photo' src='{b.get('photo')}'>")
        lines.append("</header>")
    else:
        lines.append("<header>")
        lines.append("<div class='head-left'>")
        lines.append(f"<h1 class='name'>{esc(b.get('name'))}</h1><p class='subtitle'>{esc(b.get('title'))}</p>")
        lines.append(f"<div class='contact-inline'>{esc(b.get('phone'))} ｜ {esc(b.get('email'))} ｜ {esc(b.get('location'))}</div>")
        lines.append("</div>")
        if has_photo:
            lines.append(f"<img class='photo' src='{b.get('photo')}'>")
        lines.append("</header>")

    for sec in resume.get("sections", []):
        if not sec.get("visible", True):
            continue
        lines.append(f"<h2>{esc(sec.get('title'))}</h2>")
        for it in sec.get("items", []):
            lines.append("<div class='item'>")
            head = f"<span>{esc(it.get('heading'))}</span>"
            if it.get("date"):
                head += f"<span class='date'>{esc(it.get('date'))}</span>"
            lines.append(f"<div class='item-head'>{head}</div>")
            if it.get("subheading"):
                lines.append(f"<div class='stack'>{esc(it.get('subheading'))}</div>")
            if it.get("bullets"):
                lines.append("<ul>")
                for bl in it["bullets"]:
                    if bl.get("highlight"):
                        lines.append(f"<li><strong>{esc(bl['highlight'])}</strong>：{esc(bl.get('text',''))}</li>")
                    else:
                        lines.append(f"<li>{esc(bl.get('text',''))}</li>")
                lines.append("</ul>")
            lines.append("</div>")
    lines.append("</div></body></html>")
    return "\n".join(lines)


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
