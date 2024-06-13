#!/bin/bash

# Description: Script to get the latest feedly articles and store them in the database.
#     Articles are only stored if they are not already in the database.

# Requirements:
# - Docker must be installed, and the docker daemon running on the host machine.
# - The script is intended for use with MacOS and Linux systems.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

# Initialise MongoDB.
chmod +x "$SCRIPT_DIR/mongo.sh"
$SCRIPT_DIR/mongo.sh --start

# Ensure repo is in PythonPath for imports.
export PYTHONPATH=$PYTHONPATH:$PARENT_DIR

# Run the feedly pipeline
python3 $SCRIPT_DIR/ingestion_pipeline.py $PARENT_DIR