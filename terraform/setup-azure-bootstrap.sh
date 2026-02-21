#!/usr/bin/env bash
#
# One-time Azure bootstrap setup for Aero-offers infrastructure.
# Creates resources that are prerequisites for Terraform to run:
# - Platform resource group (not managed by Terraform)
# - Terraform state storage (storage account, blob container)
# - GitHub Actions identity (managed identity, role assignment, federated credentials)
#
# All commands are idempotent - safe to re-run.
# Run this script once before first terraform apply.
#
set -euo pipefail

# Configuration
RESOURCE_GROUP="rg-aerooffers-platform"
STORAGE_ACCOUNT="staeroofferstfstate"
CONTAINER_NAME="tfstate"
LOCATION="westeurope"
SUBSCRIPTION_ID="fc0aabe8-4670-4289-90f7-c4cc116552db"
GITHUB_REPO="lwitkowski/aero-offers"

IDENTITY_NAME="id-aerooffers-github"

echo "=== Aero-offers Azure Bootstrap ==="
echo ""

# Ensure we're logged in and using the right subscription
az account set --subscription "$SUBSCRIPTION_ID"
echo "Using subscription: $(az account show --query name -o tsv)"
echo ""

# =============================================================================
# PART 1: Terraform State Storage
# =============================================================================
echo "=== Part 1: Terraform State Storage ==="

echo "Creating resource group: $RESOURCE_GROUP"
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output none

if az storage account show --name "$STORAGE_ACCOUNT" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
  echo "Storage account already exists: $STORAGE_ACCOUNT"
else
  echo "Creating storage account: $STORAGE_ACCOUNT"
  az storage account create \
    --name "$STORAGE_ACCOUNT" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --sku Standard_LRS \
    --kind StorageV2 \
    --output none
fi

echo "Creating blob container: $CONTAINER_NAME"
az storage container create \
  --name "$CONTAINER_NAME" \
  --account-name "$STORAGE_ACCOUNT" \
  --output none

echo "Terraform state storage ready: $STORAGE_ACCOUNT/$CONTAINER_NAME/"
echo ""

# =============================================================================
# PART 2: GitHub Actions Identity
# =============================================================================
echo "=== Part 2: GitHub Actions Identity ==="

echo "Creating managed identity: $IDENTITY_NAME"
az identity create \
  --name "$IDENTITY_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output none

# Get identity details
IDENTITY_CLIENT_ID=$(az identity show --name "$IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --query clientId -o tsv)
IDENTITY_PRINCIPAL_ID=$(az identity show --name "$IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --query principalId -o tsv)

echo "Identity Client ID: $IDENTITY_CLIENT_ID"

echo "Assigning Contributor role on subscription..."
az role assignment create \
  --assignee-object-id "$IDENTITY_PRINCIPAL_ID" \
  --assignee-principal-type ServicePrincipal \
  --role "Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID" \
  --output none

echo ""
echo "Creating federated credentials for GitHub Actions..."

# Credential for pull requests (terraform plan)
echo "  - github-pull-request"
az identity federated-credential create \
  --name "github-pull-request" \
  --identity-name "$IDENTITY_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --issuer "https://token.actions.githubusercontent.com" \
  --subject "repo:${GITHUB_REPO}:pull_request" \
  --audiences "api://AzureADTokenExchange" \
  --output none

# Credential for main branch (terraform plan on push)
echo "  - github-main-branch"
az identity federated-credential create \
  --name "github-main-branch" \
  --identity-name "$IDENTITY_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --issuer "https://token.actions.githubusercontent.com" \
  --subject "repo:${GITHUB_REPO}:ref:refs/heads/main" \
  --audiences "api://AzureADTokenExchange" \
  --output none

# Credential for production environment (terraform apply)
echo "  - github-deployment-production"
az identity federated-credential create \
  --name "github-deployment-production" \
  --identity-name "$IDENTITY_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --issuer "https://token.actions.githubusercontent.com" \
  --subject "repo:${GITHUB_REPO}:environment:production" \
  --audiences "api://AzureADTokenExchange" \
  --output none

echo ""
echo "=== Bootstrap Complete ==="
echo ""
echo "Add these secrets to GitHub repository settings:"
echo "  AZURE_CLIENT_ID:       $IDENTITY_CLIENT_ID"
echo "  AZURE_TENANT_ID:       $(az account show --query tenantId -o tsv)"
echo "  AZURE_SUBSCRIPTION_ID: $SUBSCRIPTION_ID"
echo ""
echo "Next steps:"
echo "  1. Add the above secrets to GitHub (Settings → Secrets → Actions)"
echo "  2. Create GitHub environment: 'production'"
echo "  3. Run: cd terraform && terraform init"
echo "  4. Run: terraform plan"
