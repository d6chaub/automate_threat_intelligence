# Threat Intelligence Automation
## Purpose

The initial repository is offered by feedly as a way to make custom feedly integrations via API.

The goal of the threat intelligence automation project is to make an application that summarizes, contextualizes, and ranks security threat information from feedly. It will also write threats to azure devops as actionable items.

# Developer Environment
## Conda

Currently, conda is being used to manage the runtime environment.
Eventually the repo will be installable as a python package to make import easier.
In the meantime, to make testing easier, I'm creating an activation and deactivation script in my conda env.

First, create a new conda environment and active, then run, changing the path to the repo as per your local setup:
```
LOCAL_PATH_TO_REPO_ROOT=/Users/yonah.citron/repos/automate_threat_intelligence

ACTIVATE_DIR=$CONDA_PREFIX/etc/conda/activate.d
DEACTIVATE_DIR=$CONDA_PREFIX/etc/conda/deactivate.d

mkdir -p $ACTIVATE_DIR
mkdir -p $DEACTIVATE_DIR

echo '#!/bin/sh' > $ACTIVATE_DIR/env_vars.sh
echo 'export OLD_PYTHONPATH="$PYTHONPATH"' >> $ACTIVATE_DIR/env_vars.sh
echo 'export PYTHONPATH="$LOCAL_PATH_TO_REPO_ROOT:$PYTHONPATH"' >> $ACTIVATE_DIR/env_vars.sh

echo '#!/bin/sh' > $DEACTIVATE_DIR/unset_env_vars.sh
echo 'export PYTHONPATH="$OLD_PYTHONPATH"' >> $DEACTIVATE_DIR/unset_env_vars.sh
echo 'unset OLD_PYTHONPATH' >> $DEACTIVATE_DIR/unset_env_vars.sh

chmod +x $ACTIVATE_DIR/env_vars.sh
chmod +x $DEACTIVATE_DIR/unset_env_vars.sh

```


Test (replacing 'your-env' with appropriate name):
conda deactivate
conda activate your-env
echo $PYTHONPATH  # Should show the path to your repo appended