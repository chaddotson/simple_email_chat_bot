#!/usr/bin/env python

from argparse import ArgumentParser
from logging import basicConfig, getLogger, INFO
import re
from six import PY2
from six.moves.configparser import RawConfigParser

logger = getLogger(__name__)


class FunctionRegistrar(object):
    def __init__(self):
        self._registered_handlers = {}

    def register(self, regex, response):
        def decorator(f):
            self._registered_handlers[regex] = {
                "regex": regex,
                "pattern": re.compile(regex, re.I),
                "func": f
            }

            return f

        return decorator

    def handle_message(self, message, *args, **kwargs):
        for key, handler_dict in self._registered_handlers.items():
            if handler_dict["pattern"].match(message):
                logger.info("key=%s", key)
                handler_dict["func"](message=message,
                                     regex=handler_dict["regex"],
                                     pattern=handler_dict["regex"], *args, **kwargs)


functions = FunctionRegistrar()


@functions.register(regex=".*echo", response="I heard you")
def echo(message, regex, *args, **kwargs):
    print("echo message={0} {1}".format(message, regex))



logging_config = dict(level=INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if PY2:
    logging_config['disable_existing_loggers'] = True

basicConfig(**logging_config)

functions.handle_message("echo123")
functions.handle_message("123echo")
#
#
#
#
# _function_map = []
#
#
# def register(regex, response):
#     # _function_map.append({
#     #    "regex": regex,
#     #    "pattern": re.compile(regex, re.I),
#     #    "func": f,
#     #    "response": response
#     # })
#     return f
#
#
# def test(message):
#     handlers = []
#     for item in _function_map:
#         if p.match(message):
#             handlers.append(item["func"])
#
#
# @register(regex="echo.*", response="echo")
# def echo(message):
#     print(message)
#
#
# test("echo 123")
#
