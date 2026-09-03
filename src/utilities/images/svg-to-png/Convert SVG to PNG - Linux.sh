#!/bin/sh
cd "$(dirname "$0")" || exit 1

if command -v python3 >/dev/null 2>&1; then
    python3 svg_to_png.py "$@"
    status=$?
else
    echo
    echo "Python 3 was not found."
    echo "Install Python 3.10 or newer, then run this again."
    echo
    status=1
fi

if [ "$status" -ne 0 ]; then
    printf "\nPress Enter to close..."
    read dummy
fi

exit "$status"
