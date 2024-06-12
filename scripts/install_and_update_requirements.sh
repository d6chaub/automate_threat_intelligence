#!/bin/bash
# Dev Notes: In my conda environment, I set up an alias for this script when I do 'conda activate'.


PACKAGE=$1
REQUIREMENTS_IN_PATH="/Users/yonah.citron/repos/automate_threat_intelligence/requirements.in"

if [ -z "$PACKAGE" ]; then
    echo "Usage: $0 <package>"
    exit 1
fi

# Install the package
pip install "$PACKAGE"
INSTALL_STATUS=$?

if [ $INSTALL_STATUS -ne 0 ]; then
    echo "Failed to install $PACKAGE. Exiting."
    exit 1
fi

# Add the package to requirements.in if not already present
if ! grep -q "^$PACKAGE" "$REQUIREMENTS_IN_PATH"; then
    # Ensure the file ends with a newline
    tail -c1 "$REQUIREMENTS_IN_PATH" | read -r _ || echo >> "$REQUIREMENTS_IN_PATH"
    echo "$PACKAGE" >> "$REQUIREMENTS_IN_PATH"
    echo "Added $PACKAGE to $REQUIREMENTS_IN_PATH"
else
    echo "$PACKAGE is already in $REQUIREMENTS_IN_PATH"
fi


# Sort the requirements.in file alphabetically
sort -o "$REQUIREMENTS_IN_PATH" "$REQUIREMENTS_IN_PATH"
# Delete any initial blank lines created by sorting
sed -i '' '/./,$!d' "$REQUIREMENTS_IN_PATH"
echo "Sorted $REQUIREMENTS_IN_PATH alphabetically."