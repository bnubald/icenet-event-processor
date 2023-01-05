# Create the resource group
resource "azurerm_resource_group" "this" {
  name     = "rg-${local.project_name}-evtproc"
  location = var.location
  tags     = local.tags
}

# Communications services for processing
module "communications" {
  source                       = "./communications"
  location                     = var.location
  project_name                 = local.project_name
  resource_group_name          = azurerm_resource_group.this.name
  default_tags                 = local.tags
}

# Event processing
module "processing" {
  source                       = "./processing"
  location                     = var.location
  project_name                 = local.project_name
  resource_group_name          = azurerm_resource_group.this.name
  default_tags                 = local.tags

  connection_endpoint          = module.communications.connection_string
  connection_key               = module.communications.connection_key

  data_topics                  = var.data_topics
  processing_topics            = var.processing_topics
}

