terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.37.0"
    }
  }

  backend "azurerm" {
    container_name       = "blob-icenetevtproc-terraform"
    key                  = "terraform.tfstate"
    resource_group_name  = "rg-icenetevtproc-terraform"
    storage_account_name = "sticenetevtprocterraform"
  }
}

