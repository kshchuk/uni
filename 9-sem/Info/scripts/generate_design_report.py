#!/usr/bin/env python3
"""
Generate a design-phase Markdown report with embedded PNG diagrams.

Features:
- Renders PlantUML .puml files to PNG via plantuml CLI or plantuml.jar.
- Converts DBML .dbml files into a simple PlantUML ER diagram, renders to PNG.
- Processes a Markdown template with placeholders:
  - {{PUML path/to/file.puml}}
  - {{DBML_ER path/to/file.dbml}}
and replaces them with Markdown images pointing to generated PNGs.

Usage:
  python scripts/generate_design_report.py \
    --template docs/templates/design_report_template.md \
    --out docs/design_report.md

Environment (optional):
  PLANTUML_CMD: full path to 'plantuml' CLI
  PLANTUML_JAR: full path to plantuml.jar (uses 'java -jar ...')

Outputs:
  - PNGs in docs/images/
  - Generated ER PlantUML in docs/generated/
  - Final Markdown report at --out
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
IMAGES_DIR = DOCS / "images"
GENERATED_DIR = DOCS / "generated"


def ensure_dirs() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)


def which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


class PlantUMLRenderer:
    def __init__(self, plantuml_cmd: Optional[str] = None, plantuml_jar: Optional[str] = None):
        self.cmd = plantuml_cmd or os.environ.get("PLANTUML_CMD") or which("plantuml")
        self.jar = plantuml_jar or os.environ.get("PLANTUML_JAR")

    def available(self) -> bool:
        return bool(self.cmd or self.jar)

    def render(self, puml_path: Path, out_png: Path) -> None:
        out_png.parent.mkdir(parents=True, exist_ok=True)
        produced = puml_path.parent / (puml_path.stem + ".png")
        if self.cmd:
            subprocess.check_call([self.cmd, "-tpng", str(puml_path)], cwd=puml_path.parent)
        elif self.jar:
            subprocess.check_call(["java", "-jar", self.jar, "-tpng", str(puml_path)], cwd=puml_path.parent)
        else:
            raise RuntimeError("No PlantUML renderer available")
        # Copy or move to desired images folder
        if not produced.exists():
            raise RuntimeError(f"PlantUML did not produce expected file: {produced}")
        shutil.move(str(produced), str(out_png))


DBML_TABLE_RE = re.compile(r"Table\s+(?P<name>[A-Za-z0-9_]+)\s*{(?P<body>.*?)}", re.S)
DBML_COL_RE = re.compile(r"^\s*([A-Za-z0-9_]+)\s+([^\s\[]+).*?$")
DBML_REF_INLINE_RE = re.compile(r"\[.*?ref:\s*([<>-])\s*([A-Za-z0-9_]+)\.([A-Za-z0-9_]+).*?\]")


def dbml_to_puml(dbml_path: Path) -> Tuple[str, List[Tuple[str, str]]]:
    text = dbml_path.read_text(encoding="utf-8")
    classes: Dict[str, List[str]] = {}
    rels: List[Tuple[str, str]] = []
    for m in DBML_TABLE_RE.finditer(text):
        tname = m.group("name")
        body = m.group("body")
        cols: List[str] = []
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("Indexes"):
                continue
            # column definition
            cm = DBML_COL_RE.match(line)
            if cm:
                col = cm.group(1)
                cols.append(col)
            # inline FK
            rm = DBML_REF_INLINE_RE.search(line)
            if rm:
                arrow = rm.group(1)
                ref_table = rm.group(2)
                # Normalize arrow direction: current table -> ref_table
                rels.append((tname, ref_table))
        classes[tname] = cols

    # Build PUML
    lines: List[str] = []
    lines.append("@startuml")
    lines.append("skinparam classAttributeIconSize 0")
    lines.append("hide circle")
    for t, cols in classes.items():
        lines.append(f"class {t} {{")
        for c in cols:
            lines.append(f"  {c}")
        lines.append("}")
    # Relations (deduplicate)
    seen = set()
    for a, b in rels:
        key = tuple(sorted((a, b)))
        if key in seen:
            continue
        seen.add(key)
    for a, b in sorted(seen):
        # show direction from child -> parent for readability
        lines.append(f"{a} --> {b}")
    lines.append("@enduml")
    return "\n".join(lines), rels


PUML_TAG_RE = re.compile(r"\{\{\s*PUML\s+([^}]+)\s*\}\}")
DBML_TAG_RE = re.compile(r"\{\{\s*DBML_ER\s+([^}]+)\s*\}\}")


def process_template(template_path: Path, out_md: Path, renderer: PlantUMLRenderer) -> None:
    content = template_path.read_text(encoding="utf-8")

    # Render PUML images
    def repl_puml(m):
        puml_rel = m.group(1).strip()
        puml_path = (ROOT / puml_rel).resolve()
        if not puml_path.exists():
            print(f"[WARN] PUML not found: {puml_rel}", file=sys.stderr)
            return f"`Missing: {puml_rel}`"
        out_png = IMAGES_DIR / (Path(puml_rel).stem + ".png")
        if renderer.available():
            renderer.render(Path(puml_path), out_png)
        else:
            print("[WARN] PlantUML not available; skipping render", file=sys.stderr)
        return f"![{Path(puml_rel).stem}]({os.path.relpath(out_png, out_md.parent)})"

    content = PUML_TAG_RE.sub(repl_puml, content)

    # Render DBML ER images via generated PUML
    def repl_dbml(m):
        dbml_rel = m.group(1).strip()
        dbml_path = (ROOT / dbml_rel).resolve()
        if not dbml_path.exists():
            print(f"[WARN] DBML not found: {dbml_rel}", file=sys.stderr)
            return f"`Missing: {dbml_rel}`"
        puml_text, _rels = dbml_to_puml(Path(dbml_path))
        gen_puml = GENERATED_DIR / (Path(dbml_rel).stem + "_er.puml")
        gen_puml.write_text(puml_text, encoding="utf-8")
        out_png = IMAGES_DIR / (gen_puml.stem + ".png")
        if renderer.available():
            renderer.render(gen_puml, out_png)
        else:
            print("[WARN] PlantUML not available; skipping render for DBML ER", file=sys.stderr)
        return f"![{gen_puml.stem}]({os.path.relpath(out_png, out_md.parent)})"

    content = DBML_TAG_RE.sub(repl_dbml, content)

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(content, encoding="utf-8")
    print(f"[OK] Report generated: {out_md}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate design report")
    parser.add_argument("--template", default=str(DOCS / "templates" / "design_report_template.md"))
    parser.add_argument("--out", default=str(DOCS / "design_report.md"))
    parser.add_argument("--plantuml", help="Path to plantuml CLI (optional)")
    parser.add_argument("--plantuml-jar", help="Path to plantuml.jar (optional)")
    args = parser.parse_args()

    ensure_dirs()
    renderer = PlantUMLRenderer(plantuml_cmd=args.plantuml, plantuml_jar=args.plantuml_jar)
    process_template(Path(args.template), Path(args.out), renderer)


if __name__ == "__main__":
    main()
