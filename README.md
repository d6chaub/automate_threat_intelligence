# Developer Setup
## Requirements
Before setting up the project, ensure you have Docker and Docker Compose installed on your machine. These tools are crucial for running the development and production pipelines.

Installing Docker: Visit Docker's official website for installation instructions.
Installing Docker Compose: Follow the instructions on Docker's website to install Docker Compose.

## Configuring the Environment
To run the application, specific directories and files must be set up. They are not in the repo since they contain sensitive files:

- Certificates Directory: Create a certs directory in the project root (this directory is already listed in .gitignore). You must place the shell.pem file in this directory. Download shell.pem here.
- Configuration Directory: Create a config directory in the project root and add the alerts configuration file.

# Running the Application
## Development Pipeline
To launch the development environment, use the following Docker Compose command:

```
docker-compose --profile dev up --build
```

This pipeline runs the code as well as the unit tests, and other dev dependencies.

## Production Pipeline
For the production environment, use:

```
docker-compose --profile prod up --build
```

This pipeline runs the code in a lighter environment without tests and dev dependencies.

# Local Development with Poetry
Poetry is a tool for dependency management and packaging in Python projects. It simplifies package management and virtual environment management.

## Installing Poetry
To install Poetry locally, execute the following command:

```
curl -sSL https://install.python-poetry.org | python3 -
```
For more detailed instructions, visit the official Poetry documentation.

## Using Poetry for Local Development
Once Poetry is installed, you can manage dependencies and virtual environments for your local development outside of Docker.

Adding Dependencies: To add libraries or packages as dependencies to your project, use the poetry add command.

Running the Project Locally:
To work with the project code in src, run:

```
poetry add --editable src
```
This configures the local environment to directly reflect changes made in the src directory.

# Development Dependencies
## Pre-commit Hooks
This project uses pre-commit hooks to automate certain tasks like running unit tests before each commit.

## Installing Development Dependencies for the First Time
To set up pre-commit hooks for the first time, first install the necessary dependencies:

```
poetry install
``` 


To activate the pre-commit hooks, run:

```
pre-commit install
```

## Committing Code
If the pre-commit hooks find issues, they must be resolved before the commit can proceed. This ensures all commits meet the required standards.