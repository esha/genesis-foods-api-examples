#!/usr/bin/env python3
"""
Simple SVG -> PNG converter for non-technical users.

Double-click one of the platform launcher scripts, choose one or more SVG
files, and PNG files will be created beside them.

Advanced command-line options:
  python svg_to_png.py file.svg
  python svg_to_png.py file.svg --quality high
  python svg_to_png.py file.svg --scale 2
  python svg_to_png.py file.svg --width 1600
  python svg_to_png.py file.svg --height 1200
  python svg_to_png.py file.svg --background white
  python svg_to_png.py file.svg --output-dir ./pngs
"""

from __future__ import annotations

import argparse
import importlib
import subprocess
import sys
from pathlib import Path

PACKAGE = "resvg_py>=0.5,<0.6"
QUALITY_SCALE = {
    "standard": 1.0,  # SVG's normal pixel dimensions
    "high": 2.0,      # 2x dimensions
    "ultra": 4.0,     # 4x dimensions
}


def ensure_supported_python() -> None:
    if sys.version_info < (3, 10):
        raise RuntimeError(
            "Python 3.10 or newer is required.\n"
            "Install the current Python 3 release from https://www.python.org/downloads/"
        )


def load_renderer():
    """Import resvg_py, installing it automatically on first use if necessary."""
    try:
        return importlib.import_module("resvg_py")
    except ImportError:
        print("First run: installing the SVG rendering component...")
        try:
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--disable-pip-version-check",
                    PACKAGE,
                ]
            )
        except Exception as exc:
            raise RuntimeError(
                "Could not install the SVG rendering component automatically.\n"
                f"Run this command and try again:\n\n"
                f'  "{sys.executable}" -m pip install "{PACKAGE}"'
            ) from exc

        return importlib.import_module("resvg_py")


def unique_output_path(path: Path, overwrite: bool) -> Path:
    if overwrite or not path.exists():
        return path

    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def convert_file(
    renderer,
    source: Path,
    *,
    output_dir: Path | None = None,
    quality: str = "standard",
    scale: float | None = None,
    width: int | None = None,
    height: int | None = None,
    background: str | None = None,
    overwrite: bool = False,
) -> Path:
    source = source.expanduser().resolve()

    if not source.exists():
        raise FileNotFoundError(f"File not found: {source}")
    if source.suffix.lower() not in {".svg", ".svgz"}:
        raise ValueError(f"Not an SVG file: {source.name}")

    destination_dir = output_dir.expanduser().resolve() if output_dir else source.parent
    destination_dir.mkdir(parents=True, exist_ok=True)

    output = unique_output_path(destination_dir / f"{source.stem}.png", overwrite)

    kwargs = {"svg_path": str(source)}

    # Explicit width/height takes precedence over quality/scale.
    if width is not None:
        kwargs["width"] = width
    if height is not None:
        kwargs["height"] = height

    if width is None and height is None:
        kwargs["zoom"] = scale if scale is not None else QUALITY_SCALE[quality]

    if background:
        kwargs["background"] = background

    png_bytes = renderer.svg_to_bytes(**kwargs)
    output.write_bytes(png_bytes)
    return output


def choose_files_gui() -> list[Path]:
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, simpledialog
    except ImportError as exc:
        raise RuntimeError(
            "The file picker is not available on this Python installation.\n"
            "Run the converter from a terminal and provide the SVG filename."
        ) from exc

    root = tk.Tk()
    root.withdraw()
    root.update()

    selected = filedialog.askopenfilenames(
        title="Choose SVG file(s) to convert",
        filetypes=[
            ("SVG files", "*.svg *.svgz"),
            ("All files", "*.*"),
        ],
    )

    if not selected:
        root.destroy()
        return []

    quality = simpledialog.askstring(
        "PNG quality",
        "Quality: standard, high, or ultra\n\n"
        "Standard keeps the SVG's normal size.\n"
        "High renders at 2x.\n"
        "Ultra renders at 4x.",
        initialvalue="standard",
        parent=root,
    )

    if quality is None:
        root.destroy()
        return []

    quality = quality.strip().lower()
    if quality not in QUALITY_SCALE:
        messagebox.showerror(
            "Invalid quality",
            "Please use standard, high, or ultra.",
            parent=root,
        )
        root.destroy()
        return []

    # Return quality through an attribute to keep the normal CLI path simple.
    choose_files_gui.quality = quality
    files = [Path(item) for item in selected]
    root.destroy()
    return files


choose_files_gui.quality = "standard"


def show_gui_result(outputs: list[Path], errors: list[str]) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox
    except ImportError:
        return

    root = tk.Tk()
    root.withdraw()
    root.update()

    if errors:
        text = ""
        if outputs:
            text += f"Converted {len(outputs)} file(s).\n\n"
        text += "Some files could not be converted:\n\n" + "\n".join(errors[:10])
        messagebox.showwarning("SVG to PNG", text, parent=root)
    else:
        location = outputs[0].parent if outputs else ""
        messagebox.showinfo(
            "SVG to PNG",
            f"Done. Converted {len(outputs)} file(s).\n\nSaved to:\n{location}",
            parent=root,
        )

    root.destroy()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert SVG files to PNG. With no filenames, a file picker opens."
    )
    parser.add_argument("files", nargs="*", help="SVG or SVGZ file(s) to convert")
    parser.add_argument(
        "--quality",
        choices=QUALITY_SCALE.keys(),
        default="standard",
        help="standard=1x, high=2x, ultra=4x (default: standard)",
    )
    parser.add_argument(
        "--scale",
        type=float,
        help="Custom render scale, e.g. 1.5 or 3. Overrides --quality.",
    )
    parser.add_argument("--width", type=int, help="Output width in pixels")
    parser.add_argument("--height", type=int, help="Output height in pixels")
    parser.add_argument(
        "--background",
        help='Background CSS color, e.g. "white", "#ffffff", or "transparent"',
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory for PNG files. Default: beside each SVG.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite an existing PNG instead of creating name_1.png.",
    )
    return parser.parse_args()


def main() -> int:
    try:
        ensure_supported_python()
        args = parse_args()

        gui_mode = not args.files
        files = [Path(item) for item in args.files]

        if gui_mode:
            files = choose_files_gui()
            args.quality = choose_files_gui.quality
            if not files:
                return 0

        if args.scale is not None and args.scale <= 0:
            raise ValueError("--scale must be greater than 0.")
        if args.width is not None and args.width <= 0:
            raise ValueError("--width must be greater than 0.")
        if args.height is not None and args.height <= 0:
            raise ValueError("--height must be greater than 0.")

        renderer = load_renderer()
        outputs: list[Path] = []
        errors: list[str] = []

        for file_path in files:
            try:
                output = convert_file(
                    renderer,
                    file_path,
                    output_dir=args.output_dir,
                    quality=args.quality,
                    scale=args.scale,
                    width=args.width,
                    height=args.height,
                    background=args.background,
                    overwrite=args.overwrite,
                )
                outputs.append(output)
                print(f"Created: {output}")
            except Exception as exc:
                message = f"{file_path}: {exc}"
                errors.append(message)
                print(f"ERROR: {message}", file=sys.stderr)

        if gui_mode:
            show_gui_result(outputs, errors)

        return 1 if errors else 0

    except Exception as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        try:
            import tkinter as tk
            from tkinter import messagebox

            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("SVG to PNG", str(exc), parent=root)
            root.destroy()
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
