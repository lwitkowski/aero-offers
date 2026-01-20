variable "container_registry_password" {
  description = "Container registry password (stored as secret)"
  type        = string
  sensitive   = true
}

variable "gemini_api_key" {
  description = "Gemini API key for LLM classifier (stored as secret)"
  type        = string
  sensitive   = true
}
