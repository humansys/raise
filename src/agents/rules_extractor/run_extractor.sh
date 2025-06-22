#!/bin/bash

# Script to properly set up the environment and run the rules extractor
# Usage: ./run_extractor.sh [path_to_file]
# If no file is provided, runs with default test cases

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Set PYTHONPATH to include current directory
export PYTHONPATH=$PYTHONPATH:$(pwd)
echo "PYTHONPATH set to: $PYTHONPATH"

# Set debugging flags
export DEBUG_LLM_RESPONSE=True
echo "Debug mode enabled: LLM responses will be shown"

# Enable debug logging
export LOG_LEVEL=DEBUG
echo "Log level set to DEBUG for detailed output"

# Check if a file parameter was provided
if [ "$1" ]; then
    # Verify the file exists
    if [ ! -f "$1" ]; then
        echo "Error: File not found: $1"
        exit 1
    fi
    
    echo "Processing file: $1"
    # Run the extractor with the file parameter
    python3 -m rules_extractor.extractor --file "$1"
else
    echo "No file specified. Running with default test cases."
    # Run the extractor with default test cases
    python3 -m rules_extractor.extractor
fi

# Exit with script's exit code
exit $? 