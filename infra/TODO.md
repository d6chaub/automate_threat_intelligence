
- Make sure that there's an approval stage in the CI/CD for prod:

1. Use Stages and Approvals
In your CI/CD pipeline, separate the deployment process into different stages. For example:

Build: Compile Bicep files into ARM templates.
Test: Run what-if analysis or validate the ARM templates.
Deploy: Deploy the changes to a staging environment.
Approve: Require manual approval before deploying to production.
e.g. 

trigger:
- main

stages:
- stage: Build
  jobs:
  - job: CompileBicep
    steps:
    - script: |
        az bicep build --file main.bicep
      displayName: 'Compile Bicep to ARM'

- stage: Validate
  jobs:
  - job: ValidateDeployment
    steps:
    - script: |
        az deployment group what-if --resource-group myResourceGroup --template-file main.json --parameters @my.parameters.json
      displayName: 'What-If Analysis'
    - script: |
        az deployment group validate --resource-group myResourceGroup --template-file main.json --parameters @my.parameters.json
      displayName: 'Validate ARM Template'
