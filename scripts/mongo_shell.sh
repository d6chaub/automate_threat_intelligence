#!/bin/bash
# In the docker container threat-intelligence-mongodb, connect interactively and enter 'mongosh' to start the MongoDB shell.
# Check docker is installed
if ! [ -x "$(command -v docker)" ]; then
    echo "Error: Docker is not installed." >&2
    exit 1
fi
# Check if the docker daemon is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker daemon is not running." >&2
    exit 1
fi

docker exec -it threat-intelligence-mongodb bash
