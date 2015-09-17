#!/bin/bash

file="download_water.js.last"

idx=$(cat "$file")

while [ $idx -le 1340 ]
do
  idx=$(cat "$file")
  node ../../../../../../ee-runner/ee-runner.js ../../../download_water.js real 15 mndwi $idx 1340
done
