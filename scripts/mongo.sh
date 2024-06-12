#!/bin/bash

# Requirements:
# - Docker must be installed, and the daemon running on the host machine.

# Input flags --start and --stop as params
start_flag=0
stop_flag=0

while [ "$#" -gt 0 ]; do
    case "$1" in
        --start) start_flag=1;;
        --stop) stop_flag=1;;
        *) echo "Unknown parameter passed: $1. Must pass either --start or --stop flag."; exit 1;;
    esac
    shift
done

if [ $start_flag -eq 1 ] && [ $stop_flag -eq 1 ]; then
    echo "Error: Cannot pass both --start and --stop flags."
    exit 1
elif [ $start_flag -eq 0 ] && [ $stop_flag -eq 0 ]; then
    echo "Error: Must pass either --start or --stop flag."
    exit 1
fi


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

# Variables
PROJECT_ROOT=$(dirname $(dirname "$0"))
CONTAINER_NAME="threat-intelligence-mongodb"

if [ $start_flag -eq 1 ]; then
    # Create container if doesn't exist
    if ! [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
        docker pull mongo
        docker run -d --name $CONTAINER_NAME -p 27017:27017 -v $PROJECT_ROOT/data/mongo:/data/db mongo
        echo "MongoDB docker container '$CONTAINER_NAME' created."
    fi
    
    docker start $CONTAINER_NAME
    echo "MongoDB docker container '$CONTAINER_NAME' started."
    exit 0
fi

if [ $stop_flag -eq 1 ]; then
    # Stop the container
    docker stop $CONTAINER_NAME
    echo "MongoDB docker container '$CONTAINER_NAME' stopped."
    exit 0
fi