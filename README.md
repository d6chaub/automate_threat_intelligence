# Threat Intelligence Automation
## Purpose

The initial repository is offered by feedly as a way to make custom feedly integrations via API.

The goal of the threat intelligence automation project is to make an application that summarizes, contextualizes, and ranks security threat information from feedly. It will also write threats to azure devops as actionable items.

Sure, here's a more organized version of the documentation, starting with the setup of development dependencies.

# Developer Setup

## Development Dependencies

This project uses `pip-tools` to manage dependencies, `pre-commit` for git hooks, and `black` for code formatting. These tools and other development dependencies are listed in `dev-requirements.in`.

### Installing Development Dependencies

To set up your development environment, install the development dependencies listed in `dev-requirements.txt`:

```sh
pip install -r dev-requirements.txt
```

**dev-requirements.in**:

```plaintext
pip-tools
pre-commit
black
```

Compile `dev-requirements.in` to `dev-requirements.txt` using `pip-compile`:

```sh
pip-compile --output-file=dev-requirements.txt dev-requirements.in
```

## Python package 'pre-commit' for git hooks

To make developer workflow easier, the repo is configured to run git hooks upon commit which run unit tests and can perform other actions along the line.

The hook specifications are contained in the `.pre-commit-config.yaml` in the root of the repo.

To ensure the pre-commit hooks run on your local machine, install the development dependencies (as described above), then run:

```sh
pre-commit install
```

Any failing test will block the local commit.

## Managing Dependencies with `requirements.in` and `requirements.txt`

This project uses `pip-tools` to manage dependencies, ensuring a clear and reproducible environment.

### How It Works

1. **Direct Dependencies**: The `requirements.in` file lists top-level packages.
2. **Compiled Dependencies**: The `requirements.txt` file is generated from `requirements.in` and includes all dependencies with their exact versions.

### Benefits

- **Clarity**: `requirements.in` contains only root dependencies.
- **Reproducibility**: `requirements.txt` pins all dependencies, preventing issues from updates.

 **Conda Environment Alias**:

   An alias `pip-install` can be defined in the `activate` script of your conda environment, calling `install_and_update_requirements.sh`.

   **Alias Definition**:

   The alias is added in the conda environment activation script, which is automatically executed when the environment is activated.

   **Setup**:

   - Find your conda environment activation script directory:

     ```sh
     mkdir -p $CONDA_PREFIX/etc/conda/activate.d
     ```

   - Create the activation script:

     **$CONDA_PREFIX/etc/conda/activate.d/add_to_requirements.sh**:

     ```sh
     #!/bin/bash
     alias pip-install="$PATH_TO_REPO/scripts/install_and_update_requirements.sh"
     ```

   - Make the script executable:

     ```sh
     chmod +x $CONDA_PREFIX/etc/conda/activate.d/add_to_requirements.sh
     ```

   **Usage**:

   After activating your conda environment, use the `pip-install` alias to install packages and update dependencies:

   ```sh
   pip-install <package-name>
   ```

   This command will:
   - Install the `requests` package.
   - Add `requests` to `requirements.in` if it's not already there.



### Pre-commit Hook

The `requirements.txt` file is compiled from `requirements.in` using a pre-commit hook.


# ToDo

- Write some integration testing for the a local database initially.


Add this??: Mention how it's a workaround for e.g. pytest and jupyter notebooks before I can properly install it as a package...

```
LOCAL_PATH_TO_REPO_ROOT=/Users/yonah.citron/repos/automate_threat_intelligence

ACTIVATE_DIR=$CONDA_PREFIX/etc/conda/activate.d
DEACTIVATE_DIR=$CONDA_PREFIX/etc/conda/deactivate.d

mkdir -p $ACTIVATE_DIR
mkdir -p $DEACTIVATE_DIR

echo #!/bin/sh > $ACTIVATE_DIR/env_vars.sh
echo "export OLD_PYTHONPATH=\"$PYTHONPATH\"" >> $ACTIVATE_DIR/env_vars.sh
echo "export PYTHONPATH=\"$LOCAL_PATH_TO_REPO_ROOT:$PYTHONPATH\"" >> $ACTIVATE_DIR/env_vars.sh
echo #!/bin/sh > $DEACTIVATE_DIR/unset_env_vars.sh
echo "export PYTHONPATH=\"$OLD_PYTHONPATH\"" >> $DEACTIVATE_DIR/unset_env_vars.sh
echo "unset OLD_PYTHONPATH" >> $DEACTIVATE_DIR/unset_env_vars.sh

chmod +x $ACTIVATE_DIR/env_vars.sh
chmod +x $DEACTIVATE_DIR/unset_env_vars.sh

```