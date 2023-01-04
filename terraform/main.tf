# Event processing
module "processing" {
  source                       = "./processing"
  location                     = var.location
  project_name                 = local.project_name
  default_tags                 = local.tags
}

