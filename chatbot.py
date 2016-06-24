from argparse import ArgumentParser
from configparser import RawConfigParser
from logging import basicConfig, getLogger, INFO, DEBUG
from six import PY2
from time import sleep
from werkzeug.utils import import_string



from pytools.email import IMAPReceiver, SMTPSender, make_simple_text_message


logger = getLogger(__name__)


def get_args():
    parser = ArgumentParser(description='Email-based chatbot.')
    parser.add_argument('-c', '--configuration', help='Chatbot configuration', default='chatbot.cfg')
    parser.add_argument('-v', '--verbose', help='Verbose log output', default=False, action='store_true')
    return parser.parse_args()


def get_email_content(email_message):
    email_body = ""

    for part in email_message.walk():
        if part.get_content_type() == 'text/plain':
            email_body += part.get_payload().rstrip().lstrip()

    email_from = email_message.get("from")
    email_subject = email_message.get("subject")

    return email_from, email_subject, email_body


def main():
    logging_config = dict(level=INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if PY2:
        logging_config['disable_existing_loggers'] = True

    basicConfig(**logging_config)

    args = get_args()

    if args.verbose:
        getLogger('').setLevel(DEBUG)

    config = RawConfigParser()
    config.read(args.configuration)

    chatbot = import_string(config.get("BOT", "BOT"))

    receiver = IMAPReceiver(config.get("GMAIL", "USERNAME"),
                            config.get("GMAIL", "PASSWORD"),
                            config.get("GMAIL", "IMAP_SERVER"))

    sender = SMTPSender(config.get("GMAIL", "USERNAME"),
                        config.get("GMAIL", "PASSWORD"),
                        config.get("GMAIL", "SMTP_SERVER"),
                        config.get("GMAIL", "SMTP_PORT"))

    try:
        while True:

            logger.info("Retrieving new messages")
            email_messages = receiver.get_new_emails()
            logger.info("Retrieved %d new messages", len(email_messages))

            for email_message in email_messages:
                email_from, email_subject, email_body = get_email_content(email_message)

                chatbot_response = chatbot.respond(email_body)
                logger.info("Chatting with %s: in: %s out: %s", email_from, email_body, chatbot_response)

                message = make_simple_text_message(from_address=config.get("GMAIL", "USERNAME"),
                                                   to_address=email_from,
                                                   subject=email_subject,
                                                   text=chatbot_response)

                sender.send_email(message)
                logger.info("Response complete")

            sleep(30)
    except KeyboardInterrupt:
        pass

main()
