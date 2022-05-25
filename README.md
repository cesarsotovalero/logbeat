# LogBeat

Inspired by [FileBeat](https://www.elastic.co/beats/filebeat), I would like to use Python to implement a small tool that monitors log files for error messages.

## What does LogBeat do

LogBeat monitors a folder after starting up. If there is any log (`.log`) files in the folder, LogBeat monitors them in different sub-threads. If a new log file is created in the folder after LogBeat is started, the new file should be monitored by LogBeat as well.

We assume the log files in the target folder has a specific format: `<TIMESTAMP> <SESSION_ID> <MESSAGE>`. When errors occur, the log message starts with `ERROR:`. The goal of LogBeat is to report such error messages, either to its standard output, or to a centralized database such as ElasticSearch.

Requirements for the error report:

- The order of the errors should follow the same order as the log file.
- Each report should include at most the last 3 messages for **the same session** before that error.
- Errors among different sessions are separated by `-----`.

Besides the requirements above, the implementation of LogBeat should be well-tested using proper tools.

Additional thoughts of the tool:

- It should be configurable, like the parth to the target folder or file, the format of logs, etc.
- Since it is a **monitor** instead of an **analyzer**, performance matters. What if a log file is huge, with a large number of session IDs?
- CI/CD could be applied using GitHub Actions.
- Dockerized it?

## What do I need to implement

- [X] Code skeleton
- [X] Read configurations from a file
- [X] Sub-threads management (make sure to kill all the sub-threads when LogBeat stops)
- [ ] Unit testing
- [ ] CI using GitHub Action
- [ ] Documentation