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

# Generate requirements.txt from requirements.in and install
pip-compile --output-file $PARENT_DIR/requirements.txt $PARENT_DIR/requirements.in
pip install -r $PARENT_DIR/requirements.txt

# Run the feedly pipeline
python3 $SCRIPT_DIR/ingestion_pipeline.py $PARENT_DIR

echo "Ingestion pipeline completed successfully."

echo "Run the 'mongosh' command to query the current MongoDB database."