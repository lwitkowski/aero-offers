variable "container_registry_password" {
  description = "Container registry password (stored as secret)"
  type        = string
  sensitive   = true
}
