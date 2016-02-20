#!/bin/sh

# 1-stream-ingest.sh
# Jonah Smith
# Storytelling with Streaming Data, Spring 2016
#
# This is a simple script that kicks off the Wikipedia stream ingestion process.
# Before you run it, make sure Python has the following non-standard packages installed:
#   - redis==2.10.5
#   - socketIO-client==0.5.6
# Also, make sure you have installed the Redis db server and currently have it running on
# port 6379.
#
# ingest.py is connecting to the Wikipedia websocket and ingesting the flow, outputing
# timestamps to stdout. diff.py is taking those timestamps, making sure they're in
# order, maintaining a small buffer (to account for messages received out of sequence),
# and outputting the time differences between consecutive messages to stdout.
# redis-insert.py is just taking those values and stuffing them into a redis db on
# port 6379 with an arbitrary key. This is the entire front end. Ideally, you then
# hook up a system to read all the entries in the redis db, calculate average rates
# regularly, and then do something with those (e.g. alert a human). That is accomplished
# using 2-rate-alerts.sh.

python ingest.py | python diff.py | python redis-insert.py
