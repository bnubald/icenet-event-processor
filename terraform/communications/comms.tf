resource "azurerm_communication_service" "comms" {
  name                = "${var.project_name}comms"
  resource_group_name = var.resource_group_name
  data_location       = "UK"
  tags                = local.tags
}


