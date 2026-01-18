# Note: The storage account must be created before using this backend.
# You can create it manually or use a separate bootstrap script.

terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "rg-aerooffers"
    storage_account_name = "staeroofferstfstate"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
}