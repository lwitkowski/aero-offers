# Prerequisites: run terraform/setup-azure-bootstrap.sh to create the platform
# resource group, state storage account, and GitHub Actions identity.

terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "rg-aerooffers-platform"
    storage_account_name = "staeroofferstfstate"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
}