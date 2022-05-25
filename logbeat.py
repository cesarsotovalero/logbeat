#!/usr/bin/python
# -*- coding:utf-8 -*-
# Filename: logbeat.py

import os, sys, argparse, configparser, time
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

def main(config):
    pass

if __name__ == "__main__":
    logger_format = '%(asctime)-15s %(levelname)-8s %(message)s'
    logging.basicConfig(level=logging.INFO, format=logger_format)
    args = get_args()
    main(args)