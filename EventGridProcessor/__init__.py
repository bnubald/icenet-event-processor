import json
import logging
import os
import urllib.parse as urlparser

from yaml import load

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import azure.functions as func
import xarray as xr

from EventGridProcessor.utils import send_email
import EventGridProcessor.outputs as outputs
import EventGridProcessor.checks as checks


def main(event: func.EventGridEvent):
    """

    :param event:
    """
    result = json.dumps({
        'id': event.id,
        'data': event.get_json(),
        'topic': event.topic,
        'subject': event.subject,
        'event_type': event.event_type,
    })

    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("IceNet EventGrid trigger processed an event: {}".format(result))
    configuration = None

    try:
        with open(os.environ["FORECAST_PROCESSING_CONFIG"], "r") as fh:
            configuration = load(fh, Loader=Loader)
    except KeyError:
        logging.exception("Necessary FORECAST_PROCESSING_CONFIG envvar is not "
                          "set, reverting to default email")
    except FileNotFoundError:
        logging.exception("FORECAST_PROCESSING_CONFIG file not available, "
                          "reverting to default email")
    finally:
        logging.debug("Configuration provided: {}".format(configuration))

        if configuration is None or \
                ("default_email" in configuration and
                 configuration["default_email"]):
            logging.warning("No configuration provided, or we've been "
                            "instructed to send the default event email")
            message = "IceNet Forecast: please review latest " \
                      "forecast...\n\n{}".format(result)
            send_email(event.subject, message)

    logging.info("Processing event {}".format(event.event_type))

    if event.event_type == "icenet.forecast.processed":
        logging.info("Forecast processed event received")
        subject = "IceNet Forecast has finished processing into the API"
        send_email(subject, event.subject)

    if event.event_type == "Microsoft.Storage.BlobCreated":
        logging.info("Forecast upload event received")

        local_file_path = os.path.join(os.sep, "data", os.path.basename(event.subject))
        if not os.path.exists(local_file_path):
            account_url = urlparser.urlparse(event.get_json()["url"])
            account_location = "{}://{}".format(account_url.scheme, account_url.netloc)
            logging.debug("Received {}".format(account_url))

            blob_service_client = BlobServiceClient(account_location,
                                                    credential=DefaultAzureCredential())
            container_client = blob_service_client.get_container_client(container="data")
            logging.info("Downloading blob to {}".format(local_file_path))

            with open(file=local_file_path, mode="wb") as download_file:
                download_file.write(
                    container_client.download_blob(
                        os.path.basename(event.subject)).readall())
        else:
            logging.warning("We already have {}, continuing...".format(local_file_path))

        logging.info("Opening {}".format(local_file_path))
        da = xr.open_dataset(local_file_path).sic_mean

        logging.info("Processing output configuration {}".format(configuration["outputs"]))
        for output in configuration["outputs"]:
            if hasattr(outputs, output["implementation"]):
                logging.info("Calling {} in EventGridProcessor.outputs".
                             format(output["implementation"]))
                getattr(checks, output["implementation"])(da, output)

        logging.info("Processing output configuration {}".format(configuration["checks"]))
        for check in configuration["checks"]:
            if hasattr(checks, check["implementation"]):
                logging.info("Calling {} in EventGridProcessor.checks".
                             format(check["implementation"]))
                getattr(checks, check["implementation"])(da, check)
