#!/bin/bash

usage() {
  echo "Usage: $0 --target-deployment-environment <target_environment>"
  echo "       Deploy the Azure Function for the Ingestion pipeline."
  echo "Options:"
  echo "  --target-deployment-environment   Target deployment environment ('dev' or 'prod')"
  echo "  -h, --help      Display this help message"
}



# Parse command-line arguments
while [[ "$1" != "" ]]; do
  case $1 in
    --target-deployment-environment)
      shift
      TARGET_DEPLOYMENT_ENVIRONMENT="$1"
      shift
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      usage
      exit 1
      ;;
  esac
done

# Install jq
if ! command -v jq &> /dev/null; then
  echo "jq is not installed. Installing jq..."
  sudo apt-get install jq
fi

# Set file paths
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
ROOT_DIR=$(dirname $SCRIPT_DIR)
FUNCTION_APP_DIRNAME="alerts-ingestion-func-app"
FUNCTION_APP_DIR="$ROOT_DIR/$FUNCTION_APP_DIRNAME"
SRC_DIR="$ROOT_DIR/src"
DEPLOYMENT_ARTIFACTS_ROOT_DIR="$ROOT_DIR/deployment-artifacts"
INGESTION_PIPELINE_DEPLOYMENT_ARTIFACTS_DIR="$DEPLOYMENT_ARTIFACTS_ROOT_DIR/ingestion-pipeline"

# Get from the compiled parameters file
COMPILED_PARAMETERS_FILE="$ROOT_DIR/infra/$TARGET_DEPLOYMENT_ENVIRONMENT.params.json"
RESOURCE_GROUP_NAME=$(jq -r '.parameters.resourceGroupName.value' $COMPILED_PARAMETERS_FILE)
SUBSCRIPTION_ID=$(jq -r '.parameters.subscriptionId.value' $COMPILED_PARAMETERS_FILE)
INGESTION_FUNCTION_APP_NAME=$(jq -r '.parameters.ingestionFunctionAppName.value' $COMPILED_PARAMETERS_FILE)
if [ -z "$RESOURCE_GROUP_NAME" ]; then
    echo "Error: resourceGroupName is not present in $COMPILED_PARAMETERS_FILE"
    exit 1
fi

if [ -z "$SUBSCRIPTION_ID" ]; then
    echo "Error: subscriptionId is not present in $COMPILED_PARAMETERS_FILE"
    exit 1
fi

if [ -z "$INGESTION_FUNCTION_APP_NAME" ]; then
    echo "Error: ingestionFunctionAppName is not present in $COMPILED_PARAMETERS_FILE"
    exit 1
fi


# Prepare the deployment function with dependencies packaged.
mkdir -p $INGESTION_PIPELINE_DEPLOYMENT_ARTIFACTS_DIR
# Make a folder for this deployment
TIMESTAMP=$(date +%Y%m%d%H%M%S)
DEPLOYMENT_DIR="$INGESTION_PIPELINE_DEPLOYMENT_ARTIFACTS_DIR/$TIMESTAMP"
mkdir -p $DEPLOYMENT_DIR


# Copy the function app dir to the deployment folder
cp -r $FUNCTION_APP_DIR $DEPLOYMENT_DIR
# copy in src folder to deployment dir
DEPLOYMENT_DIR_WITH_DEPENDENCIES="$DEPLOYMENT_DIR/$FUNCTION_APP_DIRNAME"
cp -r $SRC_DIR/. $DEPLOYMENT_DIR_WITH_DEPENDENCIES



# ____             _               _   _            _____                 _   _                  _                
#|  _ \  ___ _ __ | | ___  _   _  | |_| |__   ___  |  ___|   _ _ __   ___| |_(_) ___  _ __      / \   _ __  _ __  
#| | | |/ _ \ '_ \| |/ _ \| | | | | __| '_ \ / _ \ | |_ | | | | '_ \ / __| __| |/ _ \| '_ \    / _ \ | '_ \| '_ \ 
#| |_| |  __/ |_) | | (_) | |_| | | |_| | | |  __/ |  _|| |_| | | | | (__| |_| | (_) | | | |  / ___ \| |_) | |_) |
#|____/ \___| .__/|_|\___/ \__, |  \__|_| |_|\___| |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_| /_/   \_\ .__/| .__/ 
#           |_|            |___/                                                                     |_|   |_|    

az account set --subscription $SUBSCRIPTION_ID

prev_pwd=$(pwd)
cd $DEPLOYMENT_DIR_WITH_DEPENDENCIES
func azure functionapp publish $INGESTION_FUNCTION_APP_NAME --build remote
cd $prev_pwd