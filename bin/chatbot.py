#!/usr/bin/env python3

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
    parser.add_argument('-g', '--generate', help='Generate sample chatbot configuration', default=False, action='store_true')
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


def _generate_sample_configuration():
    sample_config = RawConfigParser()

    sample_config.add_section("BOT")
    sample_config.set("BOT", "BOT", "nltk.chat.zen.zen_chatbot")
    sample_config.set("BOT", "SLEEP", 120)

    sample_config.add_section("EMAIL")
    sample_config.set("EMAIL", "USERNAME", None)
    sample_config.set("EMAIL", "PASSWORD", None)
    sample_config.set("EMAIL", "IMAP_SERVER", None)
    sample_config.set("EMAIL", "SMTP_SERVER", None)
    sample_config.set("EMAIL", "SMTP_PORT", 587)

    return sample_config


def main():
    logging_config = dict(level=INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if PY2:
        logging_config['disable_existing_loggers'] = True

    basicConfig(**logging_config)

    args = get_args()

    if args.verbose:
        getLogger('').setLevel(DEBUG)

    config = RawConfigParser()

    if args.generate:
        with open(args.configuration, "w") as f:
            _generate_sample_configuration().write(f)
        return

    config.read(args.configuration)

    chatbot = import_string(config.get("BOT", "BOT"))

    sleep_timeout = config.getint("BOT", "SLEEP")

    receiver = IMAPReceiver(config.get("EMAIL", "USERNAME"),
                            config.get("EMAIL", "PASSWORD"),
                            config.get("EMAIL", "IMAP_SERVER"))

    sender = SMTPSender(config.get("EMAIL", "USERNAME"),
                        config.get("EMAIL", "PASSWORD"),
                        config.get("EMAIL", "SMTP_SERVER"),
                        config.get("EMAIL", "SMTP_PORT"))

    try:
        while True:

            logger.info("Retrieving new messages")
            email_messages = receiver.get_new_emails()
            logger.info("Retrieved %d new messages", len(email_messages))

            for email_message in email_messages:
                email_from, email_subject, email_body = get_email_content(email_message)

                chatbot_response = chatbot.respond(email_body)
                logger.info("Chatting with %s: in: %s out: %s", email_from, email_body, chatbot_response)

                message = make_simple_text_message(from_address=config.get("EMAIL", "USERNAME"),
                                                   to_address=email_from,
                                                   subject=email_subject,
                                                   text=chatbot_response)

                sender.send_email(message)
                logger.info("Response complete")

            sleep(sleep_timeout)
    except KeyboardInterrupt:
        return

main()
