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
# Local variables
locals {
  tags = merge(
    {
      "module" = "processing"
    },
    var.default_tags,
  )
  version   = yamldecode(file("../azfunctions/config.yaml"))["version"]
  functions = yamldecode(file("../azfunctions/config.yaml"))["functions"]
  app_name  = "app-${var.project_name}-event-processing"
  # https://docs.microsoft.com/en-us/azure/azure-functions/functions-premium-plan#available-instance-skus
  # ElasticPremium  EP1  1 core   3.5  GB RAM
  # ElasticPremium  EP2  2 core   7    GB RAM
  # ElasticPremium  EP3  4 core  14    GB RAM
  # app_sku_category = "ElasticPremium"
  app_sku          = "EP1"
}

