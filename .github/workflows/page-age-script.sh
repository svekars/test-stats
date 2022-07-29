#!/bin/bash

git ls-tree -r main --name-only | grep -E '.*\.(md|csv|svg)' | while read filename; do
  echo "$(git log -1 --date=short --format="%ad" -- $filename) $filename";
done | sort -r | tr  " " ","  > file.csv
