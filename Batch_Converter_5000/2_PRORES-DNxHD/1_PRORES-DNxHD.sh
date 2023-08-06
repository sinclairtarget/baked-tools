#!/bin/bash

set -e

indir="$PWD/In"

if [[ ! -e $indir ]]; then
    echo "No In/ directory could be found. Expected it to exist at $indir."
    exit 1
fi

mkdir -p Out/

for i in In/*.mov;
do
    ffmpeg -i "$i" -c:v dnxhd -vf "scale=1920:1080,fps=24,format=yuv422p"\
        -b:v 145M "Out/${i##*/}"
done
