# poll_stats.py
# Jonah Smith
# Storytelling with Streaming Data, Spring 2016
#
#

import json
from sys import stdout
from time import sleep
import util

# Repeat the averaging indefinitely.
while 1:
    entropy = util.entropy()
    rate = util.rate()

    print(json.dumps({'entropy': entropy, 'rate': rate}))
    stdout.flush()

    sleep(1)
