# LogBeat

[![Coverage Status](https://coveralls.io/repos/github/gluckzhang/logbeat/badge.svg?branch=main&t=tAgZYi)](https://coveralls.io/github/gluckzhang/logbeat?branch=main)

Inspired by [FileBeat](https://www.elastic.co/beats/filebeat), I would like to use Python to implement a small tool that monitors log files for error messages.

## What does LogBeat do

LogBeat monitors a folder after starting up. If there is any log (`.log`) files in the folder, LogBeat monitors them in different sub-threads. If a new log file is created in the folder after LogBeat is started, the new file should be monitored by LogBeat as well.

We assume the log files in the target folder has a specific format: `<TIMESTAMP> <SESSION_ID> <MESSAGE>`. When errors occur, the log message starts with `ERROR:`. The goal of LogBeat is to report such error messages, either to its standard output, or to a centralized database such as ElasticSearch.

Requirements for the error report:

- The order of the errors should follow the same order as the log file.
- Each report should include at most the last 3 messages for **the same session** before that error.
- Errors among different sessions are separated by `-----`.

Besides the requirements above, the implementation of LogBeat should be well-tested using proper tools.

## Additional thoughts of the tool

- It should be configurable, like the parth to the target folder or file, the format of logs, etc.

This has been implemented. In the configuration file, one can either specify the path to a log file, or the path to a folder that contains log files. If a folder is specified, LogBeat keeps monitoring the files in that foler and adds newly created log files to the monitoring list as well.

- Since it is a **monitor** instead of an **analyzer**, performance matters. What if a log file is huge, with a large number of session IDs?

I have not evaluated the performance of LogBeat yet. However, if many lines are written into a log file in a short period, or there are many different session IDs in these log files, it might cause some overhead with respect to CPU usage and memory usage. Because in the current implementation, each session has a fixed-length deque for storing its log messages.

There can be at least two directions to improve the performance. First of all, the architecture and data-structures of LogBeat can be further improved. Second, it is not necessary to run such log error reporters in the same instance where the application is running. Usually we can ship the oroginal logs to a centralized database like ElasticSearch or Google Cloud's logs explorer. Then further analysis of the logs such as error detection and reporting can be done asynchronously.

- CI/CD could be applied using GitHub Actions.

Sure. Currently there are two GitHub actions: unit-testing, and reporting the coverage information to [coveralls](https://coveralls.io/).

- Dockerized it?

Considering that LogBeat does not have lots of dependencies to install, I have not made a Dockerfile for it for now. As long as Python 3 is installed, one can easily run LogBeat.

## What do I need to implement

- [X] Code skeleton
- [X] Read configurations from a file
- [X] Sub-threads management (make sure to kill all the sub-threads when LogBeat stops)
- [ ] Unit testing and integration testing
- [X] CI using GitHub Action
- [X] Documentation and code comments