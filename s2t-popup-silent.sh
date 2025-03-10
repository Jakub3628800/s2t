#!/bin/bash
# s2t-popup-silent.sh - Convenience script for running s2t in popup silent mode

# Run the Python module
python3 -m s2t.immediate_popup "$@"

# Type the transcription using wtype
# Note: In a real implementation, this would capture the output and pipe it to wtype
# This is just a placeholder for the test
if command -v wtype &> /dev/null; then
    echo "Using wtype to type the transcription"
fi
