provider "azurerm" {
  features {}
  use_oidc        = true
  subscription_id = local.subscription_id
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = local.resource_group_name
  location = local.location
}

# Container App Environment
resource "azurerm_container_app_environment" "production" {
  name                = local.container_app_environment_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
}

# Container App (API)
resource "azurerm_container_app" "api" {
  name                         = local.container_app_name
  container_app_environment_id = azurerm_container_app_environment.production.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"
  workload_profile_name        = "Consumption"

  ingress {
    external_enabled = true
    target_port      = 8080
    transport        = "auto"
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  registry {
    server               = local.container_registry_server
    username             = local.container_registry_username
    password_secret_name = "registry-password"
  }

  secret {
    name  = "registry-password"
    value = var.container_registry_password
  }

  secret {
    name  = "db-credential"
    value = azurerm_cosmosdb_account.main.primary_key
  }

  template {
    min_replicas = local.container_app_min_replicas
    max_replicas = local.container_app_max_replicas

    container {
      name   = local.container_app_name
      image  = "${local.container_registry_server}/${local.container_registry_username}/aerooffers-api:${local.docker_image_tag}"
      cpu    = local.container_app_cpu
      memory = "${local.container_app_memory}Gi"

      env {
        name  = "COSMOSDB_URL"
        value = azurerm_cosmosdb_account.main.endpoint
      }

      env {
        name  = "COSMOSDB_DB_NAME"
        value = local.cosmosdb_database_name
      }

      env {
        name        = "COSMOSDB_CREDENTIAL"
        secret_name = "db-credential"
      }
    }
  }
}

# Container App Job (Scheduled Job)
resource "azurerm_container_app_job" "update_offers" {
  name                         = local.container_app_job_name
  container_app_environment_id = azurerm_container_app_environment.production.id
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  workload_profile_name        = "Consumption"

  replica_timeout_in_seconds = local.job_replica_timeout

  registry {
    server               = local.container_registry_server
    username             = local.container_registry_username
    password_secret_name = "registry-password"
  }

  secret {
    name  = "registry-password"
    value = var.container_registry_password
  }

  secret {
    name  = "db-credential"
    value = azurerm_cosmosdb_account.main.primary_key
  }

  secret {
    name  = "gemini-api-key"
    value = var.gemini_api_key
  }

  schedule_trigger_config {
    cron_expression          = local.job_cron_expression
    parallelism              = 1
    replica_completion_count = 1
  }

  template {
    container {
      name   = local.container_app_job_name
      image  = "${local.container_registry_server}/${local.container_registry_username}/aerooffers-api:${local.docker_image_tag}"
      cpu    = local.container_app_job_cpu
      memory = "${local.container_app_job_memory}Gi"

      command = ["sh", "./run_update_offers.sh"]

      env {
        name  = "COSMOSDB_URL"
        value = azurerm_cosmosdb_account.main.endpoint
      }

      env {
        name  = "COSMOSDB_DB_NAME"
        value = local.cosmosdb_database_name
      }

      env {
        name        = "COSMOSDB_CREDENTIAL"
        secret_name = "db-credential"
      }

      env {
        name        = "GEMINI_API_KEY"
        secret_name = "gemini-api-key"
      }
    }
  }
}

# Cosmos DB Account
resource "azurerm_cosmosdb_account" "main" {
  name                = local.cosmosdb_account_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  free_tier_enabled = true

  consistency_policy {
    consistency_level       = "Session"
    max_interval_in_seconds = 5
    max_staleness_prefix    = 100
  }

  geo_location {
    location          = azurerm_resource_group.main.location
    failover_priority = 0
  }
}

# Cosmos DB Database
resource "azurerm_cosmosdb_sql_database" "main" {
  name                = local.cosmosdb_database_name
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
}

# Static Web App
resource "azurerm_static_web_app" "ui" {
  name                = local.static_web_app_name
  resource_group_name = azurerm_resource_group.main.name
  location            = "Central US"
  sku_tier            = "Free"
  sku_size            = "Free"
}

# Static Web App Custom Domain
#resource "azurerm_static_web_app_custom_domain" "ui" {
#  static_web_app_id = azurerm_static_web_app.ui.id
#  domain_name       = "aerooffers.pl"
#  validation_type   = "dns-txt-token"
#}


# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {
  name                = local.log_analytics_workspace_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}


# github integration
resource "azurerm_user_assigned_identity" "github" {
  name                = "id-aerooffers-github"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
}

resource "azurerm_role_assignment" "github_contributor" {
  principal_id         = azurerm_user_assigned_identity.github.principal_id
  scope                = azurerm_resource_group.main.id
  role_definition_name = "Contributor"
}

# used for terraform plan in the pipelines in pull request builds
resource "azurerm_federated_identity_credential" "github-pull-request" {
  name                = "github-pull-request"
  resource_group_name = azurerm_resource_group.main.name
  audience            = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  parent_id           = azurerm_user_assigned_identity.github.id
  subject             = "repo:${local.github_repo}:pull_request"
}

# used for terraform plan in the pipelines for main branch
resource "azurerm_federated_identity_credential" "github-main-branch" {
  name                = "github-main-branch"
  resource_group_name = azurerm_resource_group.main.name
  audience            = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  parent_id           = azurerm_user_assigned_identity.github.id
  subject             = "repo:${local.github_repo}:ref:refs/heads/main"
}


# used for terraform apply in the pipelines
resource "azurerm_federated_identity_credential" "github-deployment-production" {
  name                = "github-deployment-production"
  resource_group_name = azurerm_resource_group.main.name
  audience            = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  parent_id           = azurerm_user_assigned_identity.github.id
  subject             = "repo:${local.github_repo}:environment:production"
}