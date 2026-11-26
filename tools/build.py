#!/usr/bin/env python3
"""Build the site for https://courses.brianjalaian.com/llm/ into _site/llm/ (that folder is what gets deployed)."""
import os, re, shutil, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
LIVE = "https://courses.brianjalaian.com"
os.chdir(ROOT)
shutil.rmtree("_build/html", ignore_errors=True)
r = subprocess.run(["jupyter-book", "build", "--html"], env={**os.environ, "BASE_URL": "/llm"}, capture_output=True, text=True)
print("\n".join(l for l in (r.stdout + r.stderr).splitlines() if "⚠" in l or "⛔" in l))
if r.returncode: sys.exit(r.stdout[-3000:] + r.stderr[-3000:])
out = ROOT / "_site/llm"
shutil.rmtree(out.parent, ignore_errors=True)
shutil.copytree("_build/html", out)
for d in ("slides", "static"): shutil.copytree(d, out / d)
# MyST writes the build machine's address into a few files
for f in out.rglob("*"):
    if f.suffix in {".html", ".xml", ".txt", ".json"}:
        s = f.read_text(errors="ignore")
        n = re.sub(r"http://localhost:\d+", LIVE, s).replace(f"{LIVE}/llm/slides/", "/llm/slides/")  # so slide links also work in the local preview
        if n != s: f.write_text(n)
# every link inside the course must work
bad = set()
for f in out.rglob("*.html"):
    if "slides" in f.parts: continue
    for u in re.findall(r'(?:href|src)="(/llm[^"#?]*)', f.read_text()):
        t = out.parent / u.lstrip("/")
        if not (t.is_file() or (t / "index.html").is_file()): bad.add(f"{f.relative_to(out)} -> {u}")
n = sum(1 for x in out.rglob("*") if x.is_file()); mb = sum(x.stat().st_size for x in out.rglob("*") if x.is_file()) / 1e6
for b in sorted(bad): print("✗ broken link:", b)
# nothing from the private folder may be published
for f in out.rglob("*"):
    if f.is_file() and f.suffix in {".html", ".md", ".json", ".ipynb"}:
        s = f.read_text(errors="ignore")
        for w in ("instructor-solution", "_SOLUTION", "CONTAINS ANSWERS", "Listen for:", "Pause the video", "::: narration", 'class="notes"', "/Users/"):
            if w in s: print("✗ private text:", f.relative_to(out), repr(w)); bad.add(w)
print(f"{n} files, {mb:.0f} MB, {len(bad)} problem(s)")
sys.exit(1 if bad else 0)
