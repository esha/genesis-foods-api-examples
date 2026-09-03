SVG TO PNG CONVERTER
====================

WHAT IT DOES
Converts SVG files into PNG images. It works on Windows, macOS, and Linux.

The first time you run it, it may briefly install the SVG rendering component.
An internet connection is needed for that first installation.

REQUIREMENT
Python 3.10 or newer.

Download Python here if needed:
https://www.python.org/downloads/


WINDOWS
1. Double-click: Convert SVG to PNG - Windows.bat
2. Choose one or more SVG files.
3. Choose quality:
      standard = normal SVG size
      high     = 2x size
      ultra    = 4x size
4. The PNG is saved in the same folder as the SVG.

You can also drag SVG files onto the .bat file.


MAC
1. Double-click: Convert SVG to PNG - macOS.command
2. Choose one or more SVG files.
3. Choose quality.
4. The PNG is saved in the same folder as the SVG.

If macOS blocks the file the first time, right-click it and choose Open.


LINUX
1. Double-click: Convert SVG to PNG - Linux.sh
   Or run: ./Convert\ SVG\ to\ PNG\ -\ Linux.sh
2. Choose one or more SVG files.
3. Choose quality.
4. The PNG is saved in the same folder as the SVG.

Some Linux distributions do not include the Tk file picker with Python.
On Ubuntu/Debian, if no file picker appears:
    sudo apt install python3-tk


DEFAULT BEHAVIOR
- Transparent SVG backgrounds stay transparent.
- Existing PNG files are NOT overwritten.
  If image.png already exists, the converter creates image_1.png.
- Multiple SVG files can be selected at once.


OPTIONAL ADVANCED OPTIONS
These are only needed if you want more control.

Examples:

  python3 svg_to_png.py logo.svg --quality high

  python3 svg_to_png.py logo.svg --scale 3

  python3 svg_to_png.py logo.svg --width 1600

  python3 svg_to_png.py logo.svg --height 1200

  python3 svg_to_png.py logo.svg --background white

  python3 svg_to_png.py logo.svg --output-dir ./pngs

  python3 svg_to_png.py logo.svg --overwrite

Width or height automatically preserves the SVG's proportions when only one is supplied.
If width or height is specified, it takes precedence over quality/scale.
