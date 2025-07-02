// Main Bicep file for Flask app deployment on Azure App Service
// This file provisions:
// - Resource Group (implicit)
// - App Service Plan
// - App Service (Web App)
// - Application Insights
// - Log Analytics Workspace
// - Key Vault
// - Site Extension for App Service


param environmentName string
param location string
param resourceGroupName string
param SQLALCHEMY_DATABASE_URI string
param UPLOAD_FOLDER string
param MAX_CONTENT_LENGTH string
param SECRET_KEY string

var resourceToken = uniqueString(subscription().id, resourceGroup().id, environmentName)
var appServicePlanName = '${environmentName}-${resourceToken}-plan'
var webAppName = '${environmentName}-${resourceToken}-webapp'
var appInsightsName = '${environmentName}-${resourceToken}-ai'
var logAnalyticsName = '${environmentName}-${resourceToken}-logs'
var keyVaultName = '${environmentName}${resourceToken}kv'

var appServicePlanName = '${environmentName}-plan'
var webAppName = '${environmentName}-webapp'
var appInsightsName = '${environmentName}-ai'
var logAnalyticsName = '${environmentName}-logs'
var keyVaultName = '${environmentName}kv'

resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
}

resource webApp 'Microsoft.Web/sites@2022-03-01' = {
  name: webAppName
  location: location
  kind: 'app'
  tags: {
    "azd-service-name": 'flask-app'
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.12'
      cors: {
        allowedOrigins: [ '*' ]
        supportCredentials: false
      }
      appSettings: [
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
        {
          name: 'SQLALCHEMY_DATABASE_URI'
          value: SQLALCHEMY_DATABASE_URI
        }
        {
          name: 'UPLOAD_FOLDER'
          value: UPLOAD_FOLDER
        }
        {
          name: 'MAX_CONTENT_LENGTH'
          value: MAX_CONTENT_LENGTH
        }
        {
          name: 'SECRET_KEY'
          value: SECRET_KEY
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
      ]
    }
    httpsOnly: true
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}': {}
    }
  }
  dependsOn: [appServicePlan, userAssignedIdentity]
// User-assigned managed identity
resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${environmentName}-${resourceToken}-identity'
  location: location
}
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2021-06-01' = {
  name: logAnalyticsName
  location: location
  sku: {
    name: 'PerGB2018'
  }
  properties: {
    retentionInDays: 30
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    accessPolicies: []
    enabledForDeployment: true
    enabledForTemplateDeployment: true
    enabledForDiskEncryption: true
  }
}

resource siteExtension 'Microsoft.Web/sites/siteextensions@2022-03-01' = {
  name: '${webAppName}/Microsoft.Web.SiteExtension.Python'
  location: location
  properties: {}
  dependsOn: [webApp]
}

output webAppName string = webApp.name
output appServicePlanName string = appServicePlan.name
output appInsightsName string = appInsights.name
output logAnalyticsName string = logAnalytics.name
output keyVaultName string = keyVault.name
output RESOURCE_GROUP_ID string = resourceGroup().id
