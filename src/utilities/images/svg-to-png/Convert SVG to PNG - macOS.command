#!/bin/bash
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
    python3 svg_to_png.py "$@"
    status=$?
else
    echo
    echo "Python 3 was not found."
    echo "Install Python from https://www.python.org/downloads/"
    echo
    status=1
fi

if [ $status -ne 0 ]; then
    echo
    read -r -p "Press Return to close..."
fi

exit $status
