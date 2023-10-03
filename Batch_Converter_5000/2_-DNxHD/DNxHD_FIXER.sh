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
    ffmpeg -i "$i" -c:v copy -c:a copy -c:s copy "Out/${i##*/}_fixed.mov"
done
