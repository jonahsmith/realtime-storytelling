#!/usr/bin/env bash
#
# Jonah Smith
# 1-backend.sh
# Assignment 3, Storytelling with Streaming Data, Spring 2016
#
# This convenience script launches the backend of the distribution collection
# system. One branch calculates time diffs between events and loads them into
# Redis, which will be used in the frontend to calculate the rate. The other
# branch extracts the title of the article that is edited and adds that to
# another Redis table, which will be used to create our distribution of edits
# over articles.

# More specifically: ingest.py connects to the Wikipedia edit stream and outputs
# edits to stdout. The output is piped into two systems: one calculates diffs
# between events, to help us calculate the rates (this branch is very similar to
# the one I created for Assignment 2). The other retrieves the title and loads
# this as a value into the database, which is used in the frontend to create the
# distribution of edits by article in english Wikipedia. The information flow is
# illustrated below:
#
#             diff.py -> insert-diff.py
#           /
# ingest.py
#           \
#             insert-distribution.py
#
# Before you run this, make sure a Redis database is running on the default
# port!

python ingest.py | tee >(python diff.py | python insert-diffs.py) >(python insert-distribution.py)
