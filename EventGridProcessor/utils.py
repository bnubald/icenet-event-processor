import functools
import json
import logging
import os

from azure.communication.email import EmailClient


def downstream_process(func):
    """Decorator for making func as a process, providing preprocessing

    :param func: callable to wrap with context
    :return:
    """
    @functools.wraps(func)
    def new_func(*args,
                 output_directory=None,
                 **kwargs):
        returnable_output = func(*args, output_directory=output_directory, **kwargs)

        if output_directory is not None:
            output_path = os.path.join(output_directory, "{}.json".format(func.__name__))
            logging.info("Output file: {}".format(output_path))

            with open(output_path, "w") as fh:
                fh.write(json.dumps(returnable_output))
        return returnable_output

    return new_func


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
        to_addr = [os.environ["COMMS_TO_EMAIL"]] if to_addr is None else to_addr
        connection_string = os.environ["COMMS_ENDPOINT"]
        client = EmailClient.from_connection_string(connection_string)

        content = {
            "subject": subject,
            "plainText": message,
            "html": "<html><p>{}</p></html>".format(message.replace("\n", "<br />")),
        }

        recipients = {"to": [dict(address=addr) for addr in to_addr]}

        message = {
            "senderAddress":    from_addr,
            "content":          content,
            "recipients":       recipients,
        }

        logging.info("send_email message:\n{}".format(message))
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
