#!/bin/bash

# Set default values
ACTION="what-if"

# Set variables
SUBSCRIPTION_ID="a3c531dd-409f-4d4a-b076-0e2020958b66"
RESOURCE_GROUP="Threat-Intelligence-Automation"

# Set file paths
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

TEMPLATE_FILE="$SCRIPT_DIR/main.bicep"
PARAMETERS_FILE="$SCRIPT_DIR/dev.params.bicepparam"
COMPILED_PARAMETERS_FILE="$SCRIPT_DIR/dev.params.json"

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

# Compile the .bicepparam file to .json .
echo "Compiling the .bicepparam file to .json..."
az bicep build-params --file $PARAMETERS_FILE --outfile $COMPILED_PARAMETERS_FILE
echo "Compiled parameters file: $COMPILED_PARAMETERS_FILE"

# Perform the action based on the specified flag
if [ "$ACTION" == "deploy" ]; then
  echo "Performing actual infrastructure deployment..."

  az deployment group create \
    --template-file $TEMPLATE_FILE \
    --parameters @$COMPILED_PARAMETERS_FILE \
    --resource-group $RESOURCE_GROUP \
    --subscription $SUBSCRIPTION_ID
  
  echo "Infrastructure deployment completed successfully."
else
  echo "Performing What-If analysis..."
  az deployment group what-if \
    --template-file $TEMPLATE_FILE \
    --parameters @$COMPILED_PARAMETERS_FILE \
    --resource-group $RESOURCE_GROUP \
    --subscription $SUBSCRIPTION_ID
fi