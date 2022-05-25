#!/usr/bin/python
# -*- coding:utf-8 -*-
# Filename: logbeat.py

import os, sys, argparse, configparser, re, time
import logging

__version__ = "0.1"

def get_args():
    parser = argparse.ArgumentParser(
        description="LogBeat, report the errors in your log files")
    parser.add_argument("-c", "--config", required=True,
        help="The config file (.ini) for LogBeat")
    args = parser.parse_args()

    if (not os.path.exists(args.config) or not os.path.isfile(args.config)):
        logging.error("LogBeat config file does not exist, or it is not a file!")

    config = configparser.ConfigParser()
    config.read(args.config)

    return config

def handle_message(message_format, timestamp_format, session_id_format, message_body_format, message):
    message_pattern = message_format
    message_pattern = message_pattern.replace("TIMESTAMP", timestamp_format)
    message_pattern = message_pattern.replace("SESSION_ID", session_id_format)
    message_pattern = message_pattern.replace("MESSAGE_BODY", message_body_format)

    message_pattern_re = re.compile(message_pattern)
    match = message_pattern_re.search(message)
    session_id = int(match.group("session_id"))
    message_body = match.group("message_body")

    if_error = True if message_body.startswith("ERROR:") else False

    return session_id, if_error, message

def main(config):
    message_format = config["LogFormat"]["message_format"]
    timestamp_format = config["LogFormat"]["timestamp_format"]
    session_id_format = config["LogFormat"]["session_id_format"]
    message_body_format = config["LogFormat"]["message_body_format"]
    number_of_messages_included = int(config["LogBeat"]["number_of_messages_included"])

    test_message = "2022-05-25 14:23:30 [120] ERROR: This is an error message!"
    logging.info(handle_message(message_format, timestamp_format, session_id_format, message_body_format, test_message))
    test_message = "2022-05-25 14:23:30 [120] This is a normal message!"
    logging.info(handle_message(message_format, timestamp_format, session_id_format, message_body_format, test_message))


if __name__ == "__main__":
    logger_format = '%(asctime)-15s %(levelname)-8s %(message)s'
    logging.basicConfig(level=logging.INFO, format=logger_format)
    args = get_args()
    main(args)