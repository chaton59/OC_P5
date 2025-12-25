#!/bin/bash
# Export Poetry dependencies to requirements.txt for HF Spaces compatibility
poetry export -f requirements.txt --output requirements.txt --without-hashes
echo "✅ requirements.txt generated from Poetry"
