import EventGridProcessor
import datetime
import logging
import sys

logging.getLogger().setLevel(logging.DEBUG)

import azure.functions as func

if __name__ == "__main__":
    # This is just easier to test locally than hooking up event grid in Azure
    subj = sys.argv[1]
    evt = func.EventGridEvent(
        id="1",
        event_time=datetime.datetime.now(),
        subject=subj,
        topic="some_topic_or_other",
        event_type="Microsoft.Storage.BlobCreated",
        data=dict(),
        data_version=""
    )
    EventGridProcessor.main(evt)

