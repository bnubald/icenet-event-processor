variable "project_name" {
    description = "Project name for resource naming"
    type    = string
}
variable "location" {
  description = "Which Azure location to build in"
  default     = "uksouth"
}

variable "default_tags" {
    description = "Default tags for resources"
    type    = map(string)
    default = {}
}
variable "resource_group_name" {
    description = "Resource group name for resource placement"
    type    = string
}

variable "connection_endpoint" {
    description = "Endpoint for messaging"
    type = string
}

variable "connection_key" {
    description = "Key for endpoint access"
    type = string
}

variable "data_topics" {
    description = "Event Grid topics for blob data changes"
    type = set(string)
    default = []
}
variable "processing_topics" {
    description = "Event Grid topics for processing changes"
    type = set(string)
    default = []
}
variable "subnet" {
    description = "Subnet to deploy in"
    type = "string"
}

# Local variables
locals {
  tags = merge(
    {
      "module" = "processing"
    },
    var.default_tags,
  )
  app_name  = "app-${var.project_name}-event-processing"
  # https://docs.microsoft.com/en-us/azure/azure-functions/functions-premium-plan#available-instance-skus
  # ElasticPremium  EP1  1 core   3.5  GB RAM
  # ElasticPremium  EP2  2 core   7    GB RAM
  # ElasticPremium  EP3  4 core  14    GB RAM
  # app_sku_category = "ElasticPremium"
  app_sku          = "EP1"
}
