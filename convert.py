#!/usr/bin/env python3
"""Generate OmniGraffle stencils from the modern AWS Architecture Icons asset packs.

Since the 2026 icon refresh, AWS ships icons as **SVG/PNG** (no more EPS) laid out
in four collections:

    Architecture-Service-Icons_*/Arch_<Category>/{16,32,48,64}/Arch_<Service>_<sz>.svg
    Resource-Icons_*/Res_<Category>/Res_<Service>_<Resource>_48.svg
        (Res_General-Icons additionally nests Res_48_Light/ and Res_48_Dark/)
    Architecture-Group-Icons_*/<Group>_32.svg            (some with a _Dark twin)
    Category-Icons_*/Arch-Category_<sz>/Arch-Category_<Name>_<sz>.svg

This replaces the old EPS pipeline (convert.sh, which used epstopdf + pdfinfo).
Each SVG is rendered to a vector PDF with `rsvg-convert` and embedded in an
OmniGraffle `.gstencil` (a directory of imageN.pdf files plus a gzipped data.plist).

Human-readable names are derived from the filenames automatically, so the large
hand-maintained meta.txt is no longer required.

Usage:
    ./convert.py aws-source-2026 26.04.30
    ./convert.py aws-source-2026 26.04.30 --combined       # + one big stencil with everything
    ./convert.py aws-source-2026 26.04.30 --only combined  # ONLY the big stencil
    ./convert.py aws-source-2026 26.04.30 --only service   # one collection
    ./convert.py aws-source-2026 26.04.30 --png            # embed PNG instead of vector PDF

Dependencies:
    rsvg-convert   (brew install librsvg)
"""

from __future__ import annotations

import argparse
import gzip
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

# --- naming -----------------------------------------------------------------

_PREFIXES = ("Arch-Category_", "Arch_", "Res_")
# trailing  _<size>  optionally followed by _Light / _Dark
_SIZE_SUFFIX = re.compile(r"_(?:16|32|48|64)(?:_(?:Light|Dark))?$", re.IGNORECASE)
_THEME_SUFFIX = re.compile(r"_(?:Light|Dark)$", re.IGNORECASE)
# collapse immediately-repeated words: "Service Service" -> "Service"
_DUP_WORDS = re.compile(r"\b(\w+)(?:\s+\1)+\b", re.IGNORECASE)
# targeted fixes for typos in AWS's own source filenames
_WORD_ALIASES = {
    "Aternate": "Alternate",   # several Aurora / RDS resource icons
    "Saas": "SaaS",            # EventBridge SaaS Partner Event
    "CopiIoT": "Copilot",      # ECS "Copilot" mangled to "CopiIoT" upstream
}


def _spaced(segment: str) -> str:
    return segment.replace("-", " ").strip()


def derive_name(stem: str) -> str:
    """Turn an icon filename stem into a human-readable label.

    Arch_Amazon-Athena_64                 -> "Amazon Athena"
    Res_Amazon-EMR_Cluster_48             -> "Amazon EMR Cluster"
    Res_Amazon-MSK_Amazon-MSK-Connect_48  -> "Amazon MSK Connect"  (de-stuttered)
    Res_AWS-Lambda_Lambda-Function_48     -> "AWS Lambda Function"  (de-stuttered)
    Res_Alert_48_Light                    -> "Alert"
    Arch-Category_Front-End-Web-Mobile_64 -> "Front End Web Mobile"
    AWS-Cloud-logo_32                     -> "AWS Cloud logo"
    """
    name = stem
    for prefix in _PREFIXES:
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    name = _SIZE_SUFFIX.sub("", name)
    name = _THEME_SUFFIX.sub("", name)

    # The stem is <Service>[_<Resource>...]. AWS frequently repeats the service
    # name inside the resource segment ("Amazon-MSK_Amazon-MSK-Connect"); drop a
    # leading repeat so the label reads cleanly.
    parts = name.split("_")
    service = _spaced(parts[0])
    rest = " ".join(_spaced(p) for p in parts[1:]).strip()
    if rest and service and rest.lower().startswith(service.lower() + " "):
        rest = rest[len(service):].strip()
    name = f"{service} {rest}".strip() if rest else service

    name = _DUP_WORDS.sub(r"\1", name)        # "Container Service Service" -> "..."
    name = re.sub(r"\s+", " ", name).strip()

    # AWS source filenames drop the "and" from the canonical IAM service name
    name = re.sub(r"\bIdentity Access Management\b",
                  "Identity and Access Management", name)
    for wrong, right in _WORD_ALIASES.items():
        name = re.sub(rf"\b{re.escape(wrong)}\b", right, name)

    if not name or name.isdigit():            # degenerate fallback
        name = _spaced(stem.replace("_", " "))
    return re.sub(r"\s+", " ", name).strip()


def is_dark(path: Path) -> bool:
    return "_dark" in path.stem.lower() or path.parent.name.lower().endswith("_dark")


# --- svg -> image -----------------------------------------------------------

_WH_RE = re.compile(r'\bwidth="([\d.]+)(?:px)?"\s+height="([\d.]+)(?:px)?"')
_VB_RE = re.compile(r'\bviewBox="[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)"')


def svg_size(svg: Path) -> tuple[float, float]:
    """Intrinsic (width, height) of an SVG in px, which equals the PDF point
    size rsvg-convert emits at 72 dpi. Falls back to viewBox, then 64x64."""
    head = svg.read_text(encoding="utf-8", errors="replace")[:1024]
    m = _WH_RE.search(head)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = _VB_RE.search(head)
    if m:
        return float(m.group(1)), float(m.group(2))
    return 64.0, 64.0


def fmt_num(n: float) -> str:
    return str(int(n)) if float(n).is_integer() else f"{n:g}"


def render(svg: Path, dest: Path, as_png: bool) -> None:
    if as_png:
        cmd = ["rsvg-convert", "-f", "png", "-o", str(dest), str(svg)]
    else:
        # 72 dpi makes 1 svg px == 1 pdf point, so Bounds derived from the SVG
        # match the embedded artwork exactly (vector -> no quality loss).
        cmd = ["rsvg-convert", "--dpi-x", "72", "--dpi-y", "72",
               "-f", "pdf", "-o", str(dest), str(svg)]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        detail = e.stderr.decode(errors="replace").strip() if e.stderr else ""
        raise RuntimeError(f"rsvg-convert failed for {svg}: {detail}") from e


# --- plist generation -------------------------------------------------------

def rtf_notes(text: str) -> str:
    """Wrap text in the minimal RTF blob OmniGraffle stores in a Notes field."""
    safe = text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
    return (
        "{\\rtf1\\ansi\\ansicpg1252\\cocoartf2512\n"
        "{\\fonttbl\\f0\\fswiss\\fcharset0 Helvetica;}\n"
        "{\\colortbl;\\red255\\green255\\blue255;}\n"
        "{\\*\\expandedcolortbl;;}\n"
        "\\pard\\tx560\\tx1120\\tx1680\\tx2240\\tx2800\\tx3360\\tx3920\\tx4480"
        "\\tx5040\\tx5600\\tx6160\\tx6720\\pardirnatural\\partightenfactor0\n\n"
        f"\\f0\\fs24 \\cf0 {safe}}}"
    )


_MAGNETS = (
    "                    <array>\n"
    "                        <string>{1, 1}</string>\n"
    "                        <string>{1, -1}</string>\n"
    "                        <string>{-1, -1}</string>\n"
    "                        <string>{-1, 1}</string>\n"
    "                        <string>{0, 1}</string>\n"
    "                        <string>{0, -1}</string>\n"
    "                        <string>{1, 0}</string>\n"
    "                        <string>{-1, 0}</string>\n"
    "                    </array>"
)


def graphic_dict(idx: int, bounds: str, name: str, notes: str) -> str:
    return f"""                <dict>
                    <key>Bounds</key>
                    <string>{bounds}</string>
                    <key>Class</key>
                    <string>ShapedGraphic</string>
                    <key>ID</key>
                    <integer>{idx + 1}</integer>
                    <key>ImageID</key>
                    <integer>{idx}</integer>
                    <key>ManualSizeImage</key>
                    <string>NO</string>
                    <key>Magnets</key>
{_MAGNETS}
                    <key>Name</key>
                    <string>{xml_escape(name)}</string>
                    <key>Notes</key>
                    <string>{xml_escape(notes)}</string>
                    <key>StretchImage</key>
                    <true/>
                    <key>Style</key>
                    <dict>
                        <key>fill</key>
                        <dict>
                            <key>Draws</key>
                            <string>NO</string>
                        </dict>
                        <key>shadow</key>
                        <dict>
                            <key>Draws</key>
                            <string>NO</string>
                        </dict>
                        <key>stroke</key>
                        <dict>
                            <key>Draws</key>
                            <string>NO</string>
                        </dict>
                    </dict>
                </dict>"""


def build_plist(items: list[dict], image_ext: str,
                canvas_w: float, canvas_h: float) -> bytes:
    """items: list of {bounds, name, notes}. Returns gzipped plist bytes."""
    n = len(items)
    cw, ch = fmt_num(canvas_w), fmt_num(canvas_h)
    graphics = "\n".join(
        graphic_dict(i + 1, it["bounds"], it["name"], it["notes"])
        for i, it in enumerate(items)
    )
    link_back = "\n".join("        <dict/>" for _ in range(n))
    image_list = "\n".join(
        f"        <string>image{i + 1}.{image_ext}</string>" for i in range(n)
    )

    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>ApplicationVersion</key>
    <array>
        <string>com.omnigroup.OmniGraffle7.MacAppStore</string>
        <string>192.21</string>
    </array>
    <key>GraphDocumentVersion</key>
    <integer>16</integer>
    <key>GuidesLocked</key>
    <string>NO</string>
    <key>GuidesVisible</key>
    <string>YES</string>
    <key>ImageCounter</key>
    <integer>{n + 1}</integer>
    <key>ImageLinkBack</key>
    <array>
{link_back}
    </array>
    <key>ImageList</key>
    <array>
{image_list}
    </array>
    <key>LinksVisible</key>
    <string>NO</string>
    <key>MagnetsVisible</key>
    <string>NO</string>
    <key>MasterSheets</key>
    <array/>
    <key>ModificationDate</key>
    <string>2026-04-30 12:00:00 +0000</string>
    <key>Modifier</key>
    <string>AWS-OmniGraffle-Stencils</string>
    <key>MovementHandleVisible</key>
    <string>NO</string>
    <key>NotesVisible</key>
    <string>NO</string>
    <key>OriginVisible</key>
    <string>NO</string>
    <key>PageBreaks</key>
    <string>NO</string>
    <key>ReadOnly</key>
    <string>NO</string>
    <key>Sheets</key>
    <array>
        <dict>
            <key>ActiveLayerIndex</key>
            <integer>0</integer>
            <key>AutoAdjust</key>
            <integer>6</integer>
            <key>AutosizingMargin</key>
            <integer>1</integer>
            <key>BackgroundGraphic</key>
            <dict>
                <key>Bounds</key>
                <string>{{{{0, 0}}, {{{cw}, {ch}}}}}</string>
                <key>Class</key>
                <string>GraffleShapes.CanvasBackgroundGraphic</string>
                <key>ID</key>
                <integer>0</integer>
                <key>Style</key>
                <dict>
                    <key>shadow</key>
                    <dict>
                        <key>Draws</key>
                        <string>NO</string>
                    </dict>
                    <key>stroke</key>
                    <dict>
                        <key>Draws</key>
                        <string>NO</string>
                    </dict>
                </dict>
            </dict>
            <key>BaseZoom</key>
            <integer>0</integer>
            <key>CanvasDimensionsOrigin</key>
            <string>{{0, 0}}</string>
            <key>CanvasOrigin</key>
            <string>{{0, 0}}</string>
            <key>CanvasSize</key>
            <string>{{{cw}, {ch}}}</string>
            <key>CanvasSizingMode</key>
            <integer>1</integer>
            <key>ColumnAlign</key>
            <integer>0</integer>
            <key>ColumnSpacing</key>
            <real>36</real>
            <key>DisplayScale</key>
            <string>1.0 pt = 1.0 px</string>
            <key>GraphicsList</key>
            <array>
{graphics}
            </array>
            <key>GridInfo</key>
            <dict>
                <key>ShowsGrid</key>
                <string>YES</string>
                <key>SnapsToGrid</key>
                <string>YES</string>
            </dict>
            <key>KeepToScale</key>
            <false/>
            <key>Layers</key>
            <array>
                <dict>
                    <key>Lock</key>
                    <false/>
                    <key>Name</key>
                    <string>Layer 1</string>
                    <key>Print</key>
                    <true/>
                    <key>View</key>
                    <true/>
                </dict>
            </array>
            <key>Orientation</key>
            <integer>2</integer>
            <key>PrintOnePage</key>
            <false/>
            <key>RowAlign</key>
            <integer>0</integer>
            <key>RowSpacing</key>
            <real>36</real>
            <key>SheetTitle</key>
            <string>Canvas 1</string>
            <key>UniqueID</key>
            <integer>1</integer>
            <key>VPages</key>
            <integer>1</integer>
        </dict>
    </array>
    <key>SmartAlignmentGuidesActive</key>
    <string>NO</string>
    <key>SmartDistanceGuidesActive</key>
    <string>NO</string>
    <key>UseEntirePage</key>
    <false/>
    <key>useNotesKey</key>
    <true/>
</dict>
</plist>
"""
    return gzip.compress(plist.encode("utf-8"))


# --- stencil assembly -------------------------------------------------------

GRID_COLS = 10
GRID_GAP = 20.0


def build_stencil(svgs: list[Path], out_dir: Path, as_png: bool) -> int:
    """Render every svg in `svgs` into a single .gstencil at out_dir."""
    if not svgs:
        return 0
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = "png" if as_png else "pdf"

    # drop stale images from a previous build so a shrunk icon set leaves no orphans
    for old in out_dir.glob("image*.*"):
        old.unlink()

    # render images (in parallel; rsvg is single-threaded per call)
    def work(arg):
        i, svg = arg
        dest = out_dir / f"image{i + 1}.{ext}"
        render(svg, dest, as_png)
        return svg_size(svg)

    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
        sizes = list(pool.map(work, enumerate(svgs)))

    # uniform cell sized to the largest icon, so mixed sizes never overlap
    cell_w = max(w for w, h in sizes) + GRID_GAP
    cell_h = max(h for w, h in sizes) + GRID_GAP

    items = []
    max_right = max_bottom = 0.0
    for i, (svg, (w, h)) in enumerate(zip(svgs, sizes)):
        col, row = i % GRID_COLS, i // GRID_COLS
        x = col * cell_w
        y = row * cell_h
        max_right = max(max_right, x + w)
        max_bottom = max(max_bottom, y + h)
        bounds = (f"{{{{{fmt_num(x)}, {fmt_num(y)}}}, "
                  f"{{{fmt_num(w)}, {fmt_num(h)}}}}}")
        name = derive_name(svg.stem)
        items.append({"bounds": bounds, "name": name, "notes": name})

    (out_dir / "data.plist").write_bytes(
        build_plist(items, ext, max_right, max_bottom))
    return len(items)


def sorted_svgs(paths) -> list[Path]:
    """Light icons only, sorted by derived name, deduped on (name)."""
    seen: dict[str, Path] = {}
    for p in sorted(paths):
        if is_dark(p):
            continue
        key = derive_name(p.stem)
        if key in seen:
            print(f"warning: name collision {key!r}: keeping {seen[key].name}, "
                  f"dropping {p.name}", file=sys.stderr)
            continue
        seen[key] = p  # first (alphabetical) wins
    return [seen[k] for k in sorted(seen, key=str.lower)]


# --- collection discovery ---------------------------------------------------

_DATE_RE = re.compile(r"_(\d{2})(\d{2})(\d{4})")  # AWS packs are dated MMDDYYYY


def _date_key(p: Path):
    m = _DATE_RE.search(p.name)
    if m:
        mm, dd, yyyy = m.groups()
        return (1, yyyy + mm + dd)  # chronological, sortable
    return (0, p.name)


def find_dir(root: Path, pattern: str) -> Path | None:
    matches = sorted(root.glob(pattern))
    if not matches:
        return None
    if len(matches) > 1:
        chosen = max(matches, key=_date_key)  # newest dated pack wins
        print(f"warning: {len(matches)} matches for {pattern!r}; using "
              f"{chosen.name}", file=sys.stderr)
        return chosen
    return matches[0]


# Each collector returns the icons it selected (light-only, deduped within the
# collection) so both the per-category build and the combined build share logic.

def collect_service(root: Path, size: str) -> list[tuple[str, list[Path]]]:
    base = find_dir(root, "Architecture-Service-Icons*")
    if not base:
        return []
    out = []
    for cat in sorted(p for p in base.iterdir() if p.is_dir()):
        size_dir = cat / size
        svgs = sorted_svgs(size_dir.glob("*.svg")) if size_dir.is_dir() else []
        if svgs:
            out.append((derive_name(cat.name) or cat.name, svgs))
    return out


def collect_resource(root: Path) -> list[tuple[str, list[Path]]]:
    base = find_dir(root, "Resource-Icons*")
    if not base:
        return []
    out = []
    for cat in sorted(p for p in base.iterdir() if p.is_dir()):
        svgs = sorted_svgs(cat.rglob("*.svg"))  # rglob handles General-Icons subdirs
        if svgs:
            out.append((derive_name(cat.name) or cat.name, svgs))
    return out


def collect_group(root: Path) -> list[Path]:
    base = find_dir(root, "Architecture-Group-Icons*")
    return sorted_svgs(base.glob("*.svg")) if base else []


def collect_category(root: Path, size: str) -> list[Path]:
    base = find_dir(root, "Category-Icons*")
    if not base:
        return []
    size_dir = find_dir(base, f"*_{size}") or find_dir(base, "*_64")
    if not size_dir or not size_dir.is_dir():
        return []
    return sorted_svgs(size_dir.glob("*.svg"))


def do_service(root: Path, out: Path, as_png: bool, size: str) -> list[str]:
    dest = out / "Architecture Service Icons"
    return [f"  Service/{label}: {build_stencil(svgs, dest / f'{label}.gstencil', as_png)}"
            for label, svgs in collect_service(root, size)]


def do_resource(root: Path, out: Path, as_png: bool) -> list[str]:
    dest = out / "Resource Icons"
    return [f"  Resource/{label}: {build_stencil(svgs, dest / f'{label}.gstencil', as_png)}"
            for label, svgs in collect_resource(root)]


def do_group(root: Path, out: Path, as_png: bool) -> list[str]:
    svgs = collect_group(root)
    if not svgs:
        return []
    return [f"  Group Icons: {build_stencil(svgs, out / 'Group Icons.gstencil', as_png)}"]


def do_category(root: Path, out: Path, as_png: bool, size: str) -> list[str]:
    svgs = collect_category(root, size)
    if not svgs:
        return []
    return [f"  Category Icons: {build_stencil(svgs, out / 'Category Icons.gstencil', as_png)}"]


def do_combined(root: Path, out: Path, as_png: bool,
                service_size: str, category_size: str) -> list[str]:
    """One big stencil holding every icon from all four collections."""
    svgs: list[Path] = []
    for _, group in collect_service(root, service_size):
        svgs += group
    for _, group in collect_resource(root):
        svgs += group
    svgs += collect_group(root)
    svgs += collect_category(root, category_size)
    if not svgs:
        return []
    n = build_stencil(svgs, out / "AWS All Icons.gstencil", as_png)
    return [f"  AWS All Icons: {n}"]


# --- main -------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=Path, help="root of the AWS icon download")
    ap.add_argument("output", type=Path, help="output directory for the .gstencil set")
    ap.add_argument("--only",
                    choices=["service", "resource", "group", "category", "combined"],
                    action="append", help="limit to one or more collections (repeatable)")
    ap.add_argument("--combined", action="store_true",
                    help="also build one big 'AWS All Icons.gstencil' with every icon")
    ap.add_argument("--service-size", default="64", choices=["16", "32", "48", "64"],
                    help="which service-icon size to embed (default 64)")
    ap.add_argument("--category-size", default="64", choices=["16", "32", "48", "64"],
                    help="which category-icon size to embed (default 64)")
    ap.add_argument("--png", action="store_true",
                    help="embed raster PNG instead of vector PDF")
    ap.add_argument("--clean", action="store_true",
                    help="remove the output directory before generating")
    args = ap.parse_args()

    if not shutil.which("rsvg-convert"):
        print("error: rsvg-convert not found. Install it with 'brew install librsvg'",
              file=sys.stderr)
        return 1
    if not args.source.is_dir():
        print(f"error: {args.source} is not a directory", file=sys.stderr)
        return 1

    want = set(args.only) if args.only else {"service", "resource", "group", "category"}
    if args.combined:
        want.add("combined")

    # each collection writes to a distinct, separable target under output
    targets = {
        "service": args.output / "Architecture Service Icons",
        "resource": args.output / "Resource Icons",
        "group": args.output / "Group Icons.gstencil",
        "category": args.output / "Category Icons.gstencil",
        "combined": args.output / "AWS All Icons.gstencil",
    }
    if args.clean:
        if args.only:  # scope the clean to just what we're (re)building
            for c in want:
                if targets[c].exists():
                    shutil.rmtree(targets[c])
        elif args.output.exists():
            shutil.rmtree(args.output)
    args.output.mkdir(parents=True, exist_ok=True)
    log: list[str] = []
    if "service" in want:
        print("Building service icons ...")
        log += do_service(args.source, args.output, args.png, args.service_size)
    if "resource" in want:
        print("Building resource icons ...")
        log += do_resource(args.source, args.output, args.png)
    if "group" in want:
        print("Building group icons ...")
        log += do_group(args.source, args.output, args.png)
    if "category" in want:
        print("Building category icons ...")
        log += do_category(args.source, args.output, args.png, args.category_size)
    if "combined" in want:
        print("Building combined stencil ...")
        log += do_combined(args.source, args.output, args.png,
                           args.service_size, args.category_size)

    print("\n".join(log))
    total = sum(int(line.rsplit(": ", 1)[1]) for line in log)
    print(f"\nDone: {len(log)} stencils, {total} icons -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
