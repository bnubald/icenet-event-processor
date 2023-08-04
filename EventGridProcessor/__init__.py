import json
import logging
import os
from yaml import load

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import azure.functions as func
import xarray as xr

from EventGridProcessor.utils import send_email
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

        if "FORECAST_INPUT_PATH" in os.environ:
            logging.warning("Overriding default forecast path to: {}".format(os.environ["FORECAST_INPUT_PATH"]))
            local_file_path = os.path.join(os.environ["FORECAST_INPUT_PATH"], os.path.basename(event.subject))
        else:
            local_file_path = os.path.join(os.sep, "data", "input", os.path.basename(event.subject))

        logging.info("Opening {}".format(local_file_path))
        da = xr.open_dataset(local_file_path).sic_mean

        for output in configuration["outputs"]:
            if hasattr(checks, output["implementation"]):
                logging.info("Calling {} in EventGridProcessor.outputs".
                             format(output["implementation"]))
                getattr(checks, output["implementation"])(da, output)

        for check in configuration["checks"]:
            if hasattr(checks, check["implementation"]):
                logging.info("Calling {} in EventGridProcessor.checks".
                             format(check["implementation"]))
                getattr(checks, check["implementation"])(da, check)

