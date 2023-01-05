import json
import logging
import os

import azure.functions as func

def main(event: func.EventGridEvent):
    result = json.dumps({
        'id': event.id,
        'data': event.get_json(),
        'topic': event.topic,
        'subject': event.subject,
        'event_type': event.event_type,
    })

    logging.info('Python EventGrid trigger processed an event: %s', result)
    logging.info("Communications endpoint: {}".format(os.environ["COMMS_ENDPOINT"]))
    
    # Upload and consume configuration for rule processing based on it 
    # https://github.com/Azure-Samples/communication-services-python-quickstarts/blob/main/send-email/send-email.py
