#!/bin/bash
set -e

echo "=== Validating K8s Manifests ==="

cd "$(dirname "$0")/../k8s"

errors=0
for f in $(find . -name "*.yaml" -type f); do
  if ! kubectl apply --dry-run=client -f "$f" > /dev/null 2>&1; then
    echo "FAIL: $f"
    errors=$((errors + 1))
  else
    echo "  OK: $f"
  fi
done

if [ $errors -gt 0 ]; then
  echo ""
  echo "FAILED: $errors manifest(s) have errors."
  exit 1
fi

echo ""
echo "All K8s manifests are valid."
