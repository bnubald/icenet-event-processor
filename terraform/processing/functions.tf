# Create the resource group
resource "azurerm_resource_group" "this" {
  name     = "rg-${var.project_name}-evtproc"
  location = var.location
  tags     = local.tags
}

# For storing logs
resource "azurerm_application_insights" "this" {
  name                = "insights-${var.project_name}-evtproc"
  location            = var.location
  resource_group_name = azurerm_resource_group.this.name
  application_type    = "other"
  tags                = local.tags
}

# Create the storage account
resource "azurerm_storage_account" "this" {
  name                     = "st${var.project_name}"
  resource_group_name      = azurerm_resource_group.this.name
  location                 = azurerm_resource_group.this.location
  account_tier             = "Standard"
  account_kind             = "StorageV2"
  account_replication_type = "LRS"
  tags                     = local.tags
}

# Storage container for deploying functions
resource "azurerm_storage_container" "this" {
  name                  = "deployments"
  storage_account_name  = azurerm_storage_account.this.name
  container_access_type = "private"
}

# Service plan that functions belong to
resource "azurerm_service_plan" "this" {
  name                         = "plan-${var.project_name}-evtproc"
  resource_group_name          = azurerm_resource_group.this.name
  location                     = var.location
  os_type                      = "Linux"
  maximum_elastic_worker_count = 2 
  sku_name                     = local.app_sku
  tags                         = local.tags
}

# Functions to be deployed
resource "azurerm_linux_function_app" "this" {
  name                       = local.app_name
  location                   = var.location
  resource_group_name        = azurerm_resource_group.this.name
  service_plan_id            = azurerm_service_plan.this.id
  storage_account_name       = azurerm_storage_account.this.name
  storage_account_access_key = azurerm_storage_account.this.primary_access_key
  site_config {
    elastic_instance_minimum  = 1
    use_32_bit_worker         = false
    application_insights_connection_string = "InstrumentationKey=${azurerm_application_insights.this.instrumentation_key}"
    application_insights_key  = "${azurerm_application_insights.this.instrumentation_key}"
    application_stack {
      python_version = "3.9"
    }
  }
  tags = local.tags
}

# Actual function deployment
resource "null_resource" "functions" {
  # These define build order
  depends_on = [azurerm_service_plan.this, azurerm_linux_function_app.this]

  # These will trigger a redeploy
  triggers = {
    functions    = "${local.version}_${join("+", [for value in local.functions : value["name"]])}"
    service_plan = "${azurerm_service_plan.this.id}_${local.app_sku}"
    function_app = "${azurerm_linux_function_app.this.id}_${local.version}"
  }

  provisioner "local-exec" {
    command = <<EOF
    echo "Waiting for other deployments to finish..."
    sleep 150
    cd ../azfunctions
    echo "Deploying functions from $(pwd)"
    func azure functionapp publish ${local.app_name} --python
    cd -
    EOF
  }
}
