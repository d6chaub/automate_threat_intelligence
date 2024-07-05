#!/bin/bash

# Default action
ACTION="what-if"

usage() {
  echo "Usage: $0 [--whatif | --deploy] --target-deployment-environment <target_environment>"
  echo "       Perform a What-If analysis or an actual deployment for the specified Azure resources."
  echo "Options:"
  echo "  --whatif        Perform a What-If analysis (default)"
  echo "  --deploy        Perform the actual deployment"
  echo "  --target-deployment-environment      Target deployment environment ('dev' or 'prod')"
  echo "  -h, --help      Display this help message"
}

# Parse command-line arguments
while [[ "$1" != "" ]]; do
  case $1 in
    --deploy)
      ACTION="deploy"
      shift
      ;;
    --whatif)
      ACTION="what-if"
      shift
      ;;
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


# Validate required parameters
if [ -z "$TARGET_DEPLOYMENT_ENVIRONMENT" ]; then
  echo "Error: The Target Deployment Environment must be provided. Options are 'dev' or 'prod'."
  echo ""
  usage
  exit 1
fi

# Set file paths
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
ROOT_DIR=$(dirname $SCRIPT_DIR)
INFRA_DIR="$ROOT_DIR/infra"
TEMPLATE_FILE="$INFRA_DIR/main.bicep"
PARAMETERS_FILE="$INFRA_DIR/$TARGET_DEPLOYMENT_ENVIRONMENT.params.bicepparam"
COMPILED_PARAMETERS_FILE="$INFRA_DIR/$TARGET_DEPLOYMENT_ENVIRONMENT.params.json"

# Compile the .bicepparam file to .json
echo "Compiling the .bicepparam file to .json..."
az bicep build-params --file $PARAMETERS_FILE --outfile $COMPILED_PARAMETERS_FILE
echo "Compiled parameters file: $COMPILED_PARAMETERS_FILE"

# Obtain parameters to set scope
RESOURCE_GROUP_NAME=$(jq -r '.parameters.resourceGroupName.value' $COMPILED_PARAMETERS_FILE)
SUBSCRIPTION_ID=$(jq -r '.parameters.subscriptionId.value' $COMPILED_PARAMETERS_FILE)


# Perform the action based on the specified flag
if [ "$ACTION" == "deploy" ]; then
  echo "*** Executing actual provisioning of live infrastructure in environment $TARGET_DEPLOYMENT_ENVIRONMENT ***"
  az deployment group create \
    --template-file $TEMPLATE_FILE \
    --parameters @$COMPILED_PARAMETERS_FILE \
    --resource-group $RESOURCE_GROUP_NAME \
    --subscription $SUBSCRIPTION_ID
  echo "Infrastructure successfully provisioned for environment $TARGET_DEPLOYMENT_ENVIRONMENT."
else
  echo "Performing What-If analysis..."
  az deployment group what-if \
    --template-file $TEMPLATE_FILE \
    --parameters @$COMPILED_PARAMETERS_FILE \
    --resource-group $RESOURCE_GROUP_NAME \
    --subscription $SUBSCRIPTION_ID
  # Maybe perform this as a separate step in deployment pipeline to allow user interaction for approval of both steps.
  az deployment group validate \
    --template-file $TEMPLATE_FILE \
    --parameters @$COMPILED_PARAMETERS_FILE \
    --resource-group $RESOURCE_GROUP_NAME \
    --subscription $SUBSCRIPTION_ID
fi
