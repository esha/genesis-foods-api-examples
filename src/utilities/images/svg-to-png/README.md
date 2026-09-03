# SVG to PNG Converter

A simple cross-platform utility for converting SVG files into PNG images on Windows, macOS, and Linux.

The first time you run it, the converter may briefly install the SVG rendering component. An internet connection is required for that first installation.

## Requirements

- Python 3.10 or newer

If Python is not already installed, download it from:

https://www.python.org/downloads/

## Windows

1. Double-click `Convert SVG to PNG - Windows.bat`.
2. Choose one or more SVG files.
3. Choose a quality level:
   - `standard` — normal SVG size
   - `high` — 2× size
   - `ultra` — 4× size
4. The PNG file is saved in the same folder as the SVG.

You can also drag one or more SVG files directly onto the `.bat` file.

## macOS

1. Double-click `Convert SVG to PNG - macOS.command`.
2. Choose one or more SVG files.
3. Choose a quality level.
4. The PNG file is saved in the same folder as the SVG.

If macOS blocks the file the first time, right-click it and choose **Open**.

## Linux

1. Double-click `Convert SVG to PNG - Linux.sh`.

   Or run:

   ```bash
   ./Convert\ SVG\ to\ PNG\ -\ Linux.sh
   ```

2. Choose one or more SVG files.
3. Choose a quality level.
4. The PNG file is saved in the same folder as the SVG.

Some Linux distributions do not include the Tk file picker with Python.

On Ubuntu or Debian, if no file picker appears, install Tk with:

```bash
sudo apt install python3-tk
```

## Default Behavior

- Transparent SVG backgrounds remain transparent.
- Existing PNG files are **not overwritten**.
  - If `image.png` already exists, the converter creates `image_1.png`.
- Multiple SVG files can be selected and converted at once.

## Optional Advanced Options

These options are only needed if you want more control.

### Quality

```bash
python3 svg_to_png.py logo.svg --quality high
```

Available values:

- `standard` — 1× size
- `high` — 2× size
- `ultra` — 4× size

### Custom Scale

```bash
python3 svg_to_png.py logo.svg --scale 3
```

### Set Output Width

```bash
python3 svg_to_png.py logo.svg --width 1600
```

### Set Output Height

```bash
python3 svg_to_png.py logo.svg --height 1200
```

### Set a Background Color

```bash
python3 svg_to_png.py logo.svg --background white
```

### Save PNGs to Another Folder

```bash
python3 svg_to_png.py logo.svg --output-dir ./pngs
```

### Overwrite an Existing PNG

```bash
python3 svg_to_png.py logo.svg --overwrite
```

## Sizing Notes

If only `--width` or `--height` is supplied, the SVG's proportions are preserved automatically.

If `--width` or `--height` is specified, it takes precedence over `--quality` and `--scale`.
