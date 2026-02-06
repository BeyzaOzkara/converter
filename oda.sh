#!/bin/bash
set -e

IN_DIR="$1"
OUT_DIR="$2"

timeout 120s xvfb-run -a \
  ODAFileConverter \
  "$IN_DIR" \
  "$OUT_DIR" \
  ACAD2000 \
  DXF \
  0 \
  1
