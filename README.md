# Project Setup and Management Guide

## Developer Setup
### Requirements
Ensure Docker and Docker Compose are installed to handle both development and production pipelines.
- **Docker**: [Installation instructions](https://www.docker.com/get-started)
- **Docker Compose**: [Installation instructions](https://docs.docker.com/compose/install/)
### Configuring the Environment
Set up necessary directories and sensitive files not tracked in the repository:
- **Certificates Directory**: Create a `certs` directory at the project root and add the `shell.pem` file. This directory is included in `.gitignore`.
- **Configuration Directory**: Create a `config` directory at the project root for configuration files.


## Running the Application
### Development Pipeline
Run the development environment with:
```bash
docker-compose --profile dev up --build
```
This setup includes unit tests and development dependencies.
### Production Pipeline
Run the production environment with:
```bash
docker-compose --profile prod up
```
This setup focuses on running the application in a lighter environment without development-specific tools.


## Local Development with Poetry
### Installing Poetry
Install Poetry for Python dependency management:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
### Managing the Project with Poetry
Use Poetry to add dependencies and manage the local Python environment:
```bash
poetry add --editable src
```


## Development Dependencies
### Pre-commit Hooks
Automate tasks like linting and tests before each commit.
```bash
poetry install
pre-commit install
```


## CI/CD and Environment Lifecycle Management
### Trunk-based Development Overview
Trunk-based Development (TBD) involves direct commits to a single main branch, facilitating rapid integration and deployment cycles, ideal for lean teams.
### CI/CD Pipeline Configuration
The pipeline supports automated deployments:
Development: Commits to main trigger deployments to a development environment.
Production: Controlled deployments via Git tags.
### Triggering a Production Deployment
#### Step-by-Step Production Deployment
1. Identify the Commit:
Use git log to find the commit hash.
```bash
git log --pretty=format:"%h - %s" -n 10
```
2. Tag the Commit:
Tag using the format prod-release-YYYYMMDD with detailed release notes.
```bash
git tag -a prod-release-YYYYMMDD <commit-hash> -m "Detailed release notes here"
git push origin prod-release-YYYYMMDD
```
This triggers the CI/CD pipeline for a controlled deployment to production.