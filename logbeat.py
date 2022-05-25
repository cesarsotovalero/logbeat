#!/usr/bin/python
# -*- coding:utf-8 -*-
# Filename: logbeat.py

import os, sys, time, argparse, configparser, re, multiprocessing, signal
from collections import deque
import logging

__version__ = "0.1"

MONITOR_THREADS = list()

def handle_sigint(sig, frame):
    global MONITOR_THREADS
    for thread in MONITOR_THREADS:
        if thread.is_alive():
            thread.terminate()
    print("Thank you for trying LogBeat!")
    exit()

def get_args():
    parser = argparse.ArgumentParser(
        description="LogBeat, report the errors in your log files")
    parser.add_argument("-c", "--config", required=True,
        help="The config file (.ini) for LogBeat")
    args = parser.parse_args()

    if (not os.path.exists(args.config) or not os.path.isfile(args.config)):
        logging.error("LogBeat config file does not exist, or it is not a file!")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(args.config)

    if config["LogBeat"]["logfile_path"] == "" and config["LogBeat"]["logfile_folder"] == "":
        logging.error("Either logfile_path or logfile_folder needs to be specified!")
        sys.exit(1)

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
        logging.error("Incorrectly formated message detected: %s"%message.encode("utf-8"))
        return (None, None, message)

    session_id = int(match.group("session_id"))
    message_body = match.group("message_body")

    if_error = True if message_body.startswith("ERROR:") else False

    return session_id, if_error, message

def generate_error_report(filepath, message_queue):
    global MONITOR_THREADS

    if len(MONITOR_THREADS) > 0:
        error_report = "(from logfile %s)\n"%filepath
    else:
        error_report = ""
    delimiter = "-----"
    while len(message_queue) > 0:
        m = message_queue.pop()
        error_report += m.rstrip() + "\n"
    error_report += delimiter

    return error_report

def file_monitor(filepath, logfile_format, handler, frequency,
            number_of_messages_included, handle_existing_lines):
    deques_for_sids = dict()
    with open(filepath) as logfile:
        if not handle_existing_lines: logfile.seek(0, 2)
        while True:
            message = logfile.readline()
            if not message:
                time.sleep(frequency)
            elif len(message.strip()) > 0:
                sid, if_error, message = handler(logfile_format, message)
                if sid != None:
                    if sid not in deques_for_sids:
                        deques_for_sids[sid] = deque(maxlen=number_of_messages_included)

                    deques_for_sids[sid].appendleft(message)
                    if if_error: print(generate_error_report(filepath, deques_for_sids[sid]))

def main(config):
    global MONITOR_THREADS

    number_of_messages_included = int(config["LogBeat"]["number_of_messages_included"])
    seconds_between_checks = float(config["LogBeat"]["seconds_between_checks"])
    handle_existing_lines = False if int(config["LogBeat"]["handle_existing_lines"]) == 0 else True
    logfile_path = config["LogBeat"]["logfile_path"]
    logfile_folder = config["LogBeat"]["logfile_folder"]
    logfile_format = config["LogFormat"]

    if logfile_path != "":
        file_monitor(logfile_path,
            logfile_format,
            message_handler,
            seconds_between_checks,
            number_of_messages_included,
            handle_existing_lines)
    elif logfile_folder != "":
        monitored_files = list()
        while True:
            for entry in os.listdir(logfile_folder):
                if os.path.isfile(os.path.join(logfile_folder, entry)):
                    filename, file_extension = os.path.splitext(entry)
                    if file_extension == ".log" and entry not in monitored_files:
                        monitor_thread = multiprocessing.Process(target=file_monitor,
                            args=(os.path.join(logfile_folder, entry),
                                logfile_format,
                                message_handler,
                                seconds_between_checks,
                                number_of_messages_included,
                                handle_existing_lines))
                        MONITOR_THREADS.append(monitor_thread)
                        monitored_files.append(entry)
                        monitor_thread.start()
            time.sleep(seconds_between_checks)
        for thread in MONITOR_THREADS:
            thread.join()

if __name__ == "__main__":
    logger_format = '%(asctime)-15s %(levelname)-8s %(message)s'
    logging.basicConfig(level=logging.INFO, format=logger_format)
    args = get_args()
    signal.signal(signal.SIGINT, handle_sigint)
    main(args)