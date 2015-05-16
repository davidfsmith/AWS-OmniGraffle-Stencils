#!/bin/sh
for f in *.eps
do
  echo "Processing $f"
  epstopdf "$f"
done
