#!/usr/bin/python
# -*- coding:utf-8 -*-
# Filename: logbeat.py

import os, sys, argparse, configparser, re, time
from collections import deque
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

def message_handler(logfile_format, message):
    message_format = logfile_format["message_format"]
    timestamp_format = logfile_format["timestamp_format"]
    session_id_format = logfile_format["session_id_format"]
    message_body_format = logfile_format["message_body_format"]

    message_pattern = message_format
    message_pattern = message_pattern.replace("TIMESTAMP", timestamp_format)
    message_pattern = message_pattern.replace("SESSION_ID", session_id_format)
    message_pattern = message_pattern.replace("MESSAGE_BODY", message_body_format)

    message_pattern_re = re.compile(message_pattern)
    match = message_pattern_re.search(message)

    if match == None:
        logging.error("Incorrectly formated message detected.")
        return None

    session_id = int(match.group("session_id"))
    message_body = match.group("message_body")

    if_error = True if message_body.startswith("ERROR:") else False

    return session_id, if_error, message

def generate_error_report(message_queue):
    error_report = ""
    delimiter = "-----"
    while len(message_queue) > 0:
        error_report += message_queue.pop()
    error_report += delimiter
    print(error_report)

def file_monitor(filepath, logfile_format, handler, frequency, number_of_messages_included):
    deques_for_sids = dict()
    with open(filepath) as logfile:
        while True:
            message = logfile.readline()
            if not message:
                time.sleep(frequency)
            else:
                sid, if_error, message = handler(logfile_format, message)
                if sid not in deques_for_sids:
                    deques_for_sids[sid] = deque(maxlen=number_of_messages_included)

                deques_for_sids[sid].appendleft(message)
                if if_error: generate_error_report(deques_for_sids[sid])

def main(config):
    number_of_messages_included = int(config["LogBeat"]["number_of_messages_included"])
    seconds_between_checks = float(config["LogBeat"]["seconds_between_checks"])
    logfile_path = config["LogBeat"]["logfile_path"]
    logfile_format = config["LogFormat"]

    file_monitor(logfile_path, logfile_format, message_handler, seconds_between_checks, number_of_messages_included)


if __name__ == "__main__":
    logger_format = '%(asctime)-15s %(levelname)-8s %(message)s'
    logging.basicConfig(level=logging.INFO, format=logger_format)
    args = get_args()
    main(args)