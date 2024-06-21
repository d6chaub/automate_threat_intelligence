#!/bin/bash

# Set default values
ACTION="what-if"
RESOURCE_GROUP="Threat-Intelligence-Automation"
TEMPLATE_FILE="main.bicep"
PARAMETERS_FILE="dev.parameters.json"
SUBSCRIPTION_ID="a3c531dd-409f-4d4a-b076-0e2020958b66"

# Function to display usage information
usage() {
  echo "Usage: $0 [--whatif | --deploy]"
  echo "       Perform a What-If analysis or an actual deployment."
  echo "       If no flag is passed, a What-If analysis is performed by default."
  echo "Options:"
  echo "  --whatif        Perform a What-If analysis (default)"
  echo "  --deploy        Perform the actual deployment"
  echo "  -h, --help      Display this help message"
}

# Parse command-line arguments
while [[ "$1" != "" ]]; do
  case $1 in
    --deploy)
      ACTION="deploy"
      ;;
    --whatif)
      ACTION="what-if"
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
  shift
done

# Perform the action based on the specified flag
if [ "$ACTION" == "deploy" ]; then
  echo "Performing actual deployment..."
  az deployment group create \
    --template-file $TEMPLATE_FILE \
    --parameters @$PARAMETERS_FILE \
    --resource-group $RESOURCE_GROUP \
    --subscription $SUBSCRIPTION_ID
else
  echo "Performing What-If analysis..."
  az deployment group what-if \
    --template-file $TEMPLATE_FILE \
    --parameters @$PARAMETERS_FILE \
    --resource-group $RESOURCE_GROUP \
    --subscription $SUBSCRIPTION_ID
fi
