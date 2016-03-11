# poll_stats.py
# Jonah Smith
# Storytelling with Streaming Data, Spring 2016
#
# This file, in an infinite loop, uses the functions in the util file to
# calculate entropy and rate based on the state of the Redis db. It takes no
# input, and emits a JSON string with the entropy and rate to stdout. These
# messages are monitored by find-anomalies.py to, maybe not surprisingly, find
# anomalies.

import json
from sys import stdout
from time import sleep
# util has our functions for calculating the entropy and rate.
import util

# Repeat the entropy and rate calculations indefinitely.
while 1:
    # Use our utility functions to calculate entropy and rate.
    entropy = util.entropy()
    rate = util.rate()

    # Dump the entropy and rate to stdout and flush the stdout so we don't end
    # up with a buffer.
    print(json.dumps({'entropy': entropy, 'rate': rate}))
    stdout.flush()

    # Rest of one second. This will give us a nice smooth function for the rate
    # and entropy values.
    sleep(1)
