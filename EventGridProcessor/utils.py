import logging
import os

from azure.communication.email import EmailClient


def send_email(subject: str,
               message: str,
               poller_wait: int = 10,
               to_addr: list = None):
    """

    :param subject:
    :param message:
    :param poller_wait:
    :param to_addr:
    """
    # https://github.com/Azure-Samples/communication-services-python-quickstarts/blob/main/send-email/send-email.py

    try:
        from_addr = os.environ["COMMS_FROM_EMAIL"]
        to_addr = os.environ["COMMS_TO_EMAIL"] if to_addr is None else to_addr
        connection_string = os.environ["COMMS_ENDPOINT"]
        client = EmailClient.from_connection_string(connection_string)

        content = {
            "subject": subject,
            "plainText": message,
            "html": "<html><p>{}</p></html>".format(message),
        }

        recipients = {"to": [{"address": to_addr}]}

        message = {
            "senderAddress":    from_addr,
            "content":          content,
            "recipients":       recipients,
        }

        poller = client.begin_send(message)

        time_elapsed = 0

        while not poller.done():
            logging.info("Email send poller status: " + poller.status())

            poller.wait(poller_wait)
            time_elapsed += poller_wait

            if time_elapsed > 18 * poller_wait:
                raise RuntimeError("Polling timed out.")

        if poller.result()["status"] == "Succeeded":
            logging.info(f"Successfully sent the email (operation id: {poller.result()['id']})")
        else:
            raise RuntimeError(str(poller.result()["error"]))
    except Exception as ex:
        logging.exception(ex)
