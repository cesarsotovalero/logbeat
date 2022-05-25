#!/usr/bin/python
# -*- coding:utf-8 -*-
# Filename: test_logbeat.py

import unittest, logging
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



if __name__ == "__main__":
    logger_format = '%(asctime)-15s %(levelname)-8s %(message)s'
    logging.basicConfig(level=logging.INFO, format=logger_format)
    unittest.main()