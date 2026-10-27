#!/usr/bin/env bash
# CI-only validation; the dedicated Jenkins image supplies the pinned Hugo.
set -euo pipefail
cd "$(dirname "$0")/.."
expected=$(cat .hugo-version)
hugo version | grep -F "v${expected}-" >/dev/null || { echo "Hugo ${expected} is required" >&2; exit 1; }
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/test_publication.py
clock=$(date -u +%Y-%m-%dT%H:%M:%SZ)
rm -rf public
hugo --minify --panicOnWarning --clock "$clock"
python3 scripts/blog_site.py verify --clock "$clock" --public public
