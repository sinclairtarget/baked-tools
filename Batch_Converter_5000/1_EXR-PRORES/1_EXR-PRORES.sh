#!/bin/bash

set -e

indir="$PWD/In"

if [[ ! -e $indir ]]; then
    echo "No In/ directory could be found. Expected it to exist at $indir."
    exit 1
fi

mkdir -p Out/

for dir in In/*;
do
    dir=${dir%*/}
    base=$(basename $dir)
    ffmpeg -y -gamma 2.2 -r 24 -f image2 -start_number 1001 -i "$dir/${base}.%04d.exr"\
        -c:v prores -vf "scale=1920:1080,fps=24,format=yuv422p"\
        Out/${dir##*/}.mov
done
