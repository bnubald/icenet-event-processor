import importlib.util
import json
import logging
import os
import sys
import urllib.parse as urlparser

from yaml import load

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import azure.functions as func

import pandas as pd
import xarray as xr

from EventGridProcessor.utils import send_email


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
        logging.warning("Necessary FORECAST_PROCESSING_CONFIG envvar is not "
                        "set, reverting to default email")
    except FileNotFoundError:
        logging.warning("FORECAST_PROCESSING_CONFIG file not available, "
                        "reverting to default email")
    finally:
        logging.debug("Configuration provided: {}".format(configuration))

        if configuration is None or \
                ("default_email" in configuration and
                 configuration["default_email"]):
            logging.info("No configuration provided, or we've been "
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
        sas_token = os.getenv("AZURE_STORAGE_SAS_TOKEN")

        local_file_path = os.path.join(os.sep, "data", os.path.basename(event.subject))
        if not os.path.exists(local_file_path):
            account_url = urlparser.urlparse(event.get_json()["url"])
            logging.debug("Received {}".format(account_url))
            if sas_token:
                sas_url = f"{account_url.scheme}://{account_url.netloc}?{sas_token}"
                blob_service_client = BlobServiceClient(sas_url)
            else:
                account_location = f"{account_url.scheme}://{account_url.netloc}"
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

        if configuration is not None:
            logging.info("Opening {}".format(local_file_path))
            ds = xr.open_dataset(local_file_path)
            fc_dt = pd.to_datetime(ds.time.values[0])

            if len(ds.time.values) > 1:
                logging.warning("Selecting only the first forecast: {}".format(fc_dt.strftime("%F")))
                ds = ds.sel(time=fc_dt)
            else:
                ds = ds.isel(time=0)

            for process_type in ["checks", "outputs"]:
                logging.info("Processing {} configuration {}".format(process_type, configuration[process_type]))

                local_outputs_dir = os.path.join(os.sep, "data", process_type, fc_dt.strftime("%F"))
                os.makedirs(local_outputs_dir, exist_ok=True)

                for process_config in configuration[process_type]:
                    spec_name = "EventGridProcessor.processes.{}".format(process_type)

                    if process_type in sys.modules:
                        logging.info("processes.{} already in sys.modules".format(process_type))
                        module = sys.modules[spec_name]
                    elif (spec := importlib.util.find_spec(spec_name)) is not None:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[spec_name] = module
                        spec.loader.exec_module(module)
                        logging.info("{} has been imported".format(process_type))
                    else:
                        raise RuntimeWarning("EventGridProcessor.{} is not available, "
                                             "you're trying to process invalid commands".format(process_type))

                    if hasattr(module, process_config["implementation"]):
                        logging.info("Calling {} in EventGridProcessor.{}".
                                     format(process_config["implementation"], process_type))
                        try:
                            getattr(module, process_config["implementation"])(ds,
                                                                              process_config,
                                                                              output_directory=local_outputs_dir)
                        except Exception as e:
                            logging.exception(e)
                    else:
                        raise RuntimeWarning("{} is not available in EventGridProcessor.{}, "
                                             "you're trying to process invalid commands".format(
                                                process_config["implementation"],
                                                process_type))
        else:
            logging.info("Not processing as we don't have a configuration")
