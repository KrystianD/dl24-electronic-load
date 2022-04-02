#!/bin/bash
cd $(dirname "$0")/../

rm -rf output
mkdir -p output
docker run \
  --rm \
  -v "$(pwd):/src:ro" \
  -v "$(pwd)/output:/dist" \
  -e "FIXUID=$UID" \
  cdrx/pyinstaller-windows \
  "bash /src/deploy/_build_in_docker.sh"
