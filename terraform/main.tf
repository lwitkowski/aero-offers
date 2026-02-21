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
  name                       = local.container_app_environment_name
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
}

# Container App (API)
resource "azurerm_container_app" "api" {
  name                         = local.container_app_name
  container_app_environment_id = azurerm_container_app_environment.production.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

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

  secret {
    name  = "storage-connection-string"
    value = azurerm_storage_account.main.primary_connection_string
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

      env {
        name  = "USE_LLM_CLASSIFIER"
        value = "true"
      }

      env {
        name        = "AZURE_STORAGE_CONNECTION_STRING"
        secret_name = "storage-connection-string"
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

# Storage Account
resource "azurerm_storage_account" "main" {
  name                     = local.storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# Storage Container for offer html pages
resource "azurerm_storage_container" "offer_pages" {
  name                  = local.offer_pages_container_name
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# Storage Management Policy for offer pages (lifecycle: archive after 7 days)
resource "azurerm_storage_management_policy" "main" {
  storage_account_id = azurerm_storage_account.main.id

  rule {
    name    = "archive-offer-pages"
    enabled = true
    filters {
      blob_types   = ["blockBlob"]
      prefix_match = ["${local.offer_pages_container_name}/"]
    }
    actions {
      base_blob {
        tier_to_archive_after_days_since_modification_greater_than = 7
      }
    }
  }
}

# Alerting
resource "azurerm_monitor_action_group" "main" {
  name                = "ag-aerooffers"
  resource_group_name = azurerm_resource_group.main.name
  short_name          = "aerooffers"

  email_receiver {
    name          = "admin"
    email_address = local.alert_email
  }
}

resource "azurerm_monitor_scheduled_query_rules_alert_v2" "job_failure" {
  name                = "alert-update-offers-job-failure"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  description         = "Fires when the update-offers scheduled job fails"

  evaluation_frequency  = "PT1H"
  window_duration       = "PT1H"
  scopes                = [azurerm_log_analytics_workspace.main.id]
  severity              = 1
  enabled               = true
  skip_query_validation = true

  criteria {
    query = <<-QUERY
      ContainerAppSystemLogs_CL
      | where ContainerAppName_s startswith "${local.container_app_job_name}"
      | where Reason_s has_any ("Failed", "Error", "BackOff", "CrashLoopBackOff")
    QUERY

    time_aggregation_method = "Count"
    threshold               = 0
    operator                = "GreaterThan"
  }

  action {
    action_groups = [azurerm_monitor_action_group.main.id]
  }
}