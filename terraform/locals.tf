locals {
  subscription_id = "fc0aabe8-4670-4289-90f7-c4cc116552db"

  resource_group_name            = "rg-aerooffers"
  container_app_environment_name = "cae-aerooffers-prod"
  log_analytics_workspace_name   = "workspace-rgaerooffersNmVR"
  static_web_app_name            = "aerooffers-ui"
  cosmosdb_account_name          = "aerooffers-cosmosdb"
  cosmosdb_database_name         = "aerooffers"
  container_app_name             = "aerooffers-api"
  container_app_job_name         = "update-offers-job"

  location = "Switzerland North"

  # Container registry configuration
  container_registry_server   = "ghcr.io"
  container_registry_username = "lwitkowski"

  github_repo = "lwitkowski/aero-offers"

  # API configuration
  container_app_cpu          = 0.25
  container_app_memory       = 0.5
  container_app_min_replicas = 1
  container_app_max_replicas = 1

  # Scheduled job configuration
  container_app_job_cpu    = 1
  container_app_job_memory = 2
  # Runs at 17 minutes past the hour, every 11 hours starting from 03:17 (e.g., 03:17, 14:17, 01:17, 12:17, 23:17, 10:17, ...)
  job_cron_expression = "17 3/11 * * *"
  job_replica_timeout = 1800

  docker_image_tag = "392fb1f"
}
