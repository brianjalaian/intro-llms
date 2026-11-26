#!/usr/bin/env python3
"""Local preview: http://localhost:3208/llm/ (same addresses as the live site)."""
import functools, http.server
from pathlib import Path
site = Path(__file__).resolve().parent.parent / "_site"
class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store"); super().end_headers()
    def do_GET(self):
        if self.path in ("", "/"):
            self.send_response(302); self.send_header("Location", "/llm/"); self.end_headers(); return
        super().do_GET()
http.server.ThreadingHTTPServer(("127.0.0.1", 3208), functools.partial(H, directory=str(site))).serve_forever()
