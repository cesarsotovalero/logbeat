#!/usr/bin/python
# -*- coding:utf-8 -*-
# Filename: test_logbeat.py

import unittest, os, io, multiprocessing, time, logging
from unittest.mock import patch
from collections import deque
import logbeat

class TestLogBeatMethods(unittest.TestCase):

    def test_message_handler(self):
        logfile_format = {
            "message_format": r"TIMESTAMP SESSION_ID MESSAGE_BODY",
            "timestamp_format": r"(?P<timestamp>\d+-\d+-\d+ \d+:\d+:\d+)",
            "session_id_format": r"\[(?P<session_id>\d+)\]",
            "message_body_format": r"(?P<message_body>[\w\W]+$)"
        }
        test_message_normal = "2022-05-25 14:23:30 [119] This is a normal message."
        session_id, if_error, message = logbeat.message_handler(logfile_format, test_message_normal)
        self.assertEqual(session_id, 119)
        self.assertFalse(if_error)
        self.assertEqual(message, test_message_normal)

        test_message_error = "2022-05-25 14:23:30 [120] ERROR: This is an error message!"
        session_id, if_error, message = logbeat.message_handler(logfile_format, test_message_error)
        self.assertEqual(session_id, 120)
        self.assertTrue(if_error)
        self.assertEqual(message, test_message_error)

        test_message_invalid = "hello world"
        session_id, if_error, message = logbeat.message_handler(logfile_format, test_message_invalid)
        self.assertIsNone(session_id)
        self.assertIsNone(if_error)
        self.assertEqual(message, test_message_invalid)

    def test_generate_error_report_only_one_message(self):
        message_queue = deque([
            "2022-05-25 14:23:30 [120] ERROR: This is an error message!"
        ])
        expected_output = "2022-05-25 14:23:30 [120] ERROR: This is an error message!\n-----"
        report = logbeat.generate_error_report("", message_queue)
        self.assertEqual(report, expected_output)

    def test_generate_error_report_two_messages(self):
        message_queue = deque([
            "2022-05-25 14:23:30 [120] ERROR: This is an error message!",
            "2022-05-25 14:23:30 [120] This is a normal message."
        ])
        expected_output = "2022-05-25 14:23:30 [120] This is a normal message.\n2022-05-25 14:23:30 [120] ERROR: This is an error message!\n-----"
        report = logbeat.generate_error_report("", message_queue)
        self.assertEqual(report, expected_output)

class IntegrationTest(unittest.TestCase):

    @patch("time.sleep", side_effect=InterruptedError)
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_single_file_monitoring(self, stdout, mocked_sleep):
        filepath = "./tests/app1.log"
        expected_output_filepath = "./tests/app1.report"
        logfile_format = {
            "message_format": r"TIMESTAMP SESSION_ID MESSAGE_BODY",
            "timestamp_format": r"(?P<timestamp>\d+-\d+-\d+ \d+:\d+:\d+)",
            "session_id_format": r"\[(?P<session_id>\d+)\]",
            "message_body_format": r"(?P<message_body>[\w\W]+$)"
        }
        handler = logbeat.message_handler
        frequency = 1
        number_of_messages_included = 3
        handle_existing_lines = 1

        try:
            logbeat.file_monitor(filepath,
                logfile_format,
                handler,
                frequency,
                number_of_messages_included,
                handle_existing_lines)
        except InterruptedError:
            pass

        report = stdout.getvalue()
        with open(expected_output_filepath, "rt") as expected:
            expected_output = expected.read()
            self.assertEqual(report, expected_output)


if __name__ == "__main__":
    logger_format = '%(asctime)-15s %(levelname)-8s %(message)s'
    logging.basicConfig(level=logging.INFO, format=logger_format)
    unittest.main()