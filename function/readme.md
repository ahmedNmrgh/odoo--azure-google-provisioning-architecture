# Azure User Provisioning System

Automated user provisioning from CSV to Microsoft Entra ID and Google Workspace.



### 1. Prerequisites
- Azure Subscription
- Azure CLI installed
- Python 3.9+

### 2. Setup Azure Resources
```bash
# Create Resource Group
az group create --name user-provisioning --location northeu

# Create Storage Account
az storage account create --name testazgoogleodoo --resource-group user-provisioning --sku Standard_LRS

# Create Container and Queue
az storage container create --name csv-uploads --account-name userprovstorage
az storage queue create --name user-sync-queue --account-name userprovstorage

# Create Function App
az functionapp create --resource-group user-provisioning \
  --consumption-plan-location northeurope \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --name user-provisioning-app \
  --storage-account userprovstorage \
  --os-type Linux
