using 'main.bicep'

param resourceEnvironmentPrefix = 'devtia00'
param defaultTags = {
  Project: 'Threat-Intelligence-Automation'
  Environment: 'dev'
  Developers: 'yonah.citron@shell.com, d.schaub@shell.com'
}
