# These variables must be passed at the command line
variable "subscription_id" {
  description = "Which Azure subscription to build in"
  type        = string
}
variable "tenant_id" {
  description = "Which Azure tenant to build in"
  type        = string
}
variable "environment" {
  description = "Environment we're building"
  default     = "dev"
}
variable "project_prefix" {
  description = "Current project prefix used to construct Azure resource names"
  default     = "icenetevt"
}
variable "location" {
  description = "Which Azure location to build in"
  default     = "uksouth"
}
# Local variables
locals {
  database_names = ["icenet"]
  project_name   = "${var.project_prefix}${var.environment}"
  tags = {
    "deployed_by" : "Terraform"
    "project" : "IceNet"
    "component" : "EventProcessor"
  }
}

