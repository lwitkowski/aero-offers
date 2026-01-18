# Terraform Infrastructure

Terraform configuration for Azure infrastructure.

## Prerequisites

- Azure CLI authenticated
- Terraform >= 1.0
- Azure AD permissions to create resources

## Setup

1. Copy `terraform.tfvars.example` to `terraform.tfvars` and fill in:
   - `container_registry_password`
   
2. Initialize: `terraform init`

3. Plan: `terraform plan`

4. Apply: `terraform apply`
