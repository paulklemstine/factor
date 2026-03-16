#!/bin/bash
# Symlink or copy images from the research directory to the website
# Run this script from anywhere: bash /home/raver1975/factor/website/link_images.sh

SRC="/home/raver1975/factor/images"
DST="/home/raver1975/factor/website/images"

# Remove old images dir and recreate
rm -rf "$DST"
mkdir -p "$DST"

# Copy all images (symlinks can break if served by some HTTP servers)
if [ -d "$SRC" ]; then
    cp "$SRC"/*.png "$DST/" 2>/dev/null
    echo "Copied $(ls "$DST"/*.png 2>/dev/null | wc -l) images to website/images/"
else
    echo "ERROR: Source directory $SRC not found"
    exit 1
fi

# Remove setup script
rm -f /home/raver1975/factor/website/setup.sh

echo "Done! Open website/index.html in a browser."
