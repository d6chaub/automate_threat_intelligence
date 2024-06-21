#!/bin/bash

# Default action
ACTION="what-if"

# Function to display usage information
usage() {
  echo "Usage: $0 [--whatif | --deploy] --subscription-id <subscription_id> --resource-group <resource_group> --target-deployment-environment <target_environment>"
  echo "       Perform a What-If analysis or an actual deployment for the specified Azure resources."
  echo "Options:"
  echo "  --whatif        Perform a What-If analysis (default)"
  echo "  --deploy        Perform the actual deployment"
  echo "  --subscription-id              Azure Subscription ID"
  echo "  --resource-group              Azure Resource Group"
  echo "  --target-deployment-environment              Target deployment environment"
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
    --subscription-id)
      shift
      SUBSCRIPTION_ID="$1"
      shift
      ;;
    --resource-group)
      shift
      RESOURCE_GROUP="$1"
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

# Validate required parameters
if [ -z "$SUBSCRIPTION_ID" ] || [ -z "$RESOURCE_GROUP" ] || [ -z "$TARGET_DEPLOYMENT_ENVIRONMENT" ]; then
  echo "Error: Subscription ID, Resource Group, and Target Deployment Environment must all be provided."
  echo ""
  usage
  exit 1
fi

# Set file paths
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
TEMPLATE_FILE="$SCRIPT_DIR/main.bicep"
PARAMETERS_FILE="$SCRIPT_DIR/$TARGET_DEPLOYMENT_ENVIRONMENT.params.bicepparam"
COMPILED_PARAMETERS_FILE="$SCRIPT_DIR/$TARGET_DEPLOYMENT_ENVIRONMENT.params.json"

# Compile the .bicepparam file to .json
echo "Compiling the .bicepparam file to .json..."
az bicep build-params --file $PARAMETERS_FILE --outfile $COMPILED_PARAMETERS_FILE
echo "Compiled parameters file: $COMPILED_PARAMETERS_FILE"

# Perform the action based on the specified flag
if [ "$ACTION" == "deploy" ]; then
  echo "*** Executing actual provisioning of live infrastructure in environment $TARGET_DEPLOYMENT_ENVIRONMENT ***"
  az deployment group create \
    --template-file $TEMPLATE_FILE \
    --parameters @$COMPILED_PARAMETERS_FILE \
    --resource-group $RESOURCE_GROUP \
    --subscription $SUBSCRIPTION_ID
  echo "Infrastructure successfully provisioned for environment $TARGET_DEPLOYMENT_ENVIRONMENT."
else
  echo "Performing What-If analysis..."
  az deployment group what-if \
    --template-file $TEMPLATE_FILE \
    --parameters @$COMPILED_PARAMETERS_FILE \
    --resource-group $RESOURCE_GROUP \
    --subscription $SUBSCRIPTION_ID
  # Maybe perform this as a separate step in deployment pipeline to allow user interaction for approval of both steps.
  az deployment group validate \
    --template-file $TEMPLATE_FILE \
    --parameters @$COMPILED_PARAMETERS_FILE \
    --resource-group $RESOURCE_GROUP \
    --subscription $SUBSCRIPTION_ID
fi
