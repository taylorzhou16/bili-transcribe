#!/bin/bash
# Bili-transcribe skill wrapper script
# This script wraps the Python script for easier invocation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "${SCRIPT_DIR}/bili_transcribe.py" "$@"
