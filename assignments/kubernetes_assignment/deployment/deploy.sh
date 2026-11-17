#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ASSIGNMENTS_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

docker build \
  -f "$SCRIPT_DIR/Dockerfile" \
  -t rpc-server:1.0 \
  "$ASSIGNMENTS_DIR"
