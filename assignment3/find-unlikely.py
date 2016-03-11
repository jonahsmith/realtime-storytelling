# find-unlikely.py
# Jonah Smith
# Assignment 3, Storytelling with Streaming Data, Spring 2016
#
# This script accepts a stream of Wikipedia edits from ingest.py (over stdin)
# and checks the probability of each one (or rather, the probability of the
# property we are looking at) against the distribution in the Redis database. If
# it is below a threshold (described below), a message is sent via stdout about
# the unusual message. These are meant to be picked up by slack.py and sent to
# the notification system.
#
# A message whose probability is less than [], as judged by the entries in the
# Redis database, is considered unlikely. I picked this probability because [].

from sys import stdin, stdout
import json
# util contains the function we have written for the rate, entropy, histogram,
# and probability calculations.
import util

# See description above for an explanation of the 'unlikely' threshold.
THRESH = 0.05

# Repeat indefinitely
while 1:
    # Capture the input from stdin, which is the stream of data from ingest.py.
    # It is dumped as JSON, so decode it.
    line = stdin.readline()
    edit = json.loads(line)

    # We are extracting the 'wiki' key, which is a unique identifier for the
    # Wikipedia that was edited.
    message = edit.get('wiki')

    # I have written a function in util that gets the probability of a
    # particular message, given the entries in the Redis database.
    prob = util.probability(message)

    # If the probability falls below our threshold, emit a message. Otherwise,
    # loop around.
    if prob < THRESH:
        # This schema (particularly the 'unlikely_message' type) is understood
        # by the slack.py file, which sends the appropriate alerts.
        alert = {
                  'type': 'unlikely_message',
                  'message': message,
                  'prob': prob
                }
        # Print the alert to stdout and flush stdout to prevent message delay
        # from buffering.
        print(json.dumps(alert))
        stdout.flush()
