provider "astronomer" {
  api_key = local.astro_api_key
}

# Define variables
variable "astro_api_key" {
  description = "Your Astronomer API key"
  type        = string
  default     = ""  # Default is empty; will use environment variable if not set
}

variable "workspace_id" {
  description = "The ID of your Astronomer workspace"
  type        = string
  default     = ""  # Default is empty; will use environment variable if not set
}

variable "deployment_name" {
  description = "The name of your Airflow deployment"
  type        = string
  default     = "example-airflow-deployment"
}

variable "executor" {
  description = "The type of executor to use (e.g., CeleryExecutor, KubernetesExecutor)"
  type        = string
  default     = "CeleryExecutor"
}

# Use environment variables for workspace_id and astro_api_key if not explicitly set
locals {
  workspace_id  = var.workspace_id != "" ? var.workspace_id : (env("ASTRO_WORKSPACE_ID") != "" ? env("ASTRO_WORKSPACE_ID") : null)
  astro_api_key = var.astro_api_key != "" ? var.astro_api_key : (env("ASTRO_API_KEY") != "" ? env("ASTRO_API_KEY") : null)
}

# Create an Astronomer deployment
resource "astronomer_deployment" "airflow_deployment" {
  workspace_id = local.workspace_id
  label        = var.deployment_name
  executor     = var.executor
  cloud_provider = "aws"
  region        = "us-west-2"
}

# Upload DAGs to the deployment
resource "astronomer_deployment_dag" "dags" {
  deployment_id = astronomer_deployment.airflow_deployment.id
  source        = "../dags" # Path to your DAGs directory
}

# Output deployment details
output "deployment_id" {
  value = astronomer_deployment.airflow_deployment.id
}

output "deployment_url" {
  value = astronomer_deployment.airflow_deployment.urls[0]
}
