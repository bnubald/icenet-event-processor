resource "azurerm_communication_service" "comms" {
  name                = "${var.project_name}comms"
  resource_group_name = var.resource_group_name
  # This cannot be UK due to email being global - US only
  # data_location       = "UK"
  data_location       = "United States"
  tags                = local.tags
}


