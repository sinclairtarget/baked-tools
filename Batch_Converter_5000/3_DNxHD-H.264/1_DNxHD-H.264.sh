#!/bin/bash

set -e

mkdir -p Out/


indir="$PWD/In"

if [[ ! -e $indir ]]; then
    echo "No In/ directory could be found. Expected it to exist at $indir."
    exit 1
fi

for i in In/*.mov;
do
    basepath=${i##*/}
    ffmpeg -i "$i" -r 24 -c:v h264 -vf "scale=1920:1080,fps=24,format=yuv420p"\
        "Out/${basepath%.mov}.mp4"
done
