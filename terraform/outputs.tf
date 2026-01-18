output "api_url" {
  description = "Fully qualified domain name of the Container App (API)"
  value       = azurerm_container_app.api.ingress[0].fqdn
}

output "cosmosdb_endpoint" {
  description = "Endpoint of the Cosmos DB account"
  value       = azurerm_cosmosdb_account.main.endpoint
}