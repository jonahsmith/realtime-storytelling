# ingest.py
# Jonah Smith
# Storytelling with Streaming Data, Spring 2016
#
# This script takes the Unix-piped stream from ingest.py, maintains a sorted
# buffer of those timestamps, and when the buffer reaches a certain threshold,
# pops off the two highest timestamps, calculates the diff, and pumps those
# diffs out of stdout. The buffer is to prevent negative time diffs, which I
# have found happens with some regularity with the Wikipedia socket.io stream.

import json
from sys import stdin, stdout
from bisect import insort

# This array is going to hold our always-sorted timestamp buffer
buf = []
while True:
    # `edit` is a single timestamp JSON from ingest.py, which represents a
    # single edit on the english Wikipedia site.
    edit = stdin.readline()
    t = json.loads(edit).get('timestamp')

    # insort(x, y), which is from the bisect package, inserts sortable y to
    # iterable x in the correct location to keep the values in x ascending.
    insort(buf, t)

    # Wait until we have more than 10 entries in the buffer...
    if len(buf) > 10:
        # Pop the last two entries from the buffer and subtract the last from
        # the second to last
        diff = buf.pop() - buf.pop()
        # dump the diff to stdout as a JSON with key 'delta'
        print(json.dumps({'delta': diff}))
        stdout.flush()
