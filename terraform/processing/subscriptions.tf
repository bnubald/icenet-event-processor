#resource "azurerm_eventgrid_system_topic_event_subscription" "data_subs" {
#  for_each            = var.data_topics
#
#  name                = "sub-${element(reverse(split("/", "${each.key}")), 0)}"
#  system_topic        = "${each.key}"
#  # This is documented as the location of the system topic, but it still throws resource not found
#  resource_group_name = "rg-icenetetldev-data"
#
#  # https://learn.microsoft.com/en-us/azure/event-grid/event-schema-blob-storage?tabs=event-grid-event-schema
#  included_event_types = [
#    "Microsoft.Storage.BlobCreated",
#    "Microsoft.Storage.DirectoryCreated"
#  ]
#
#  azure_function_endpoint {
#    function_id       =   "${azurerm_linux_function_app.this.id}/functions/EventGridProcessor"
#    max_events_per_batch = 1
#    preferred_batch_size_in_kilobytes = 64
#  }
#}

resource "azurerm_eventgrid_event_subscription" "processing_subs" {
  for_each            = var.processing_topics

  name                = "sub-${element(reverse(split("/", "${each.key}")), 0)}"
  scope               = "${each.key}"

  azure_function_endpoint {
    function_id       =   "${azurerm_linux_function_app.this.id}/functions/EventGridProcessor"
    max_events_per_batch = 1
    preferred_batch_size_in_kilobytes = 64
  }
}
