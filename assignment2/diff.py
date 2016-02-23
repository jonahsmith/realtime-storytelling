# diff.py
# Jonah Smith
# Storytelling with Streaming Data, Spring 2016
#
# This script takes the Unix-piped stream from ingest.py. It maintains a sorted
# buffer of those timestamps. When our estimate of the server time elapsed
# between the most recent and oldest observation in the buffer exceeds a certain
# threshold (five seconds), it calculates the time difference between the two
# earliest timestamps, outputs the result as a JSON to stdout, and removes the
# oldest element from the array. The buffer is to make sure that the diffs are
# based on the actual event time, and not the order in which they arrive.

import json
from sys import stdin, stdout
from bisect import insort

# This array is going to hold our always-sorted timestamp buffer
buf = []
while True:
    # `edit` is a JSON string from the stream representing an English Wikipedia
    # edit event.
    edit = stdin.readline()
    # We'll load the JSON string, and then get the 'timestamp' key, which is a
    # Unix timestamp (e.g. seconds since the epoch), according to the
    # documentation: https://www.mediawiki.org/wiki/Manual:RCFeed#Properties
    t = json.loads(edit).get('timestamp')

    # If we get a new edit notification with a timestamp lower than the lowest
    # one in the buffer, we didn't wait long enough, and we emitted a few
    # erroneous diffs. This function ensures that there's a limit to the delay
    # we'll accept, so that we don't accidentally include the old activity and
    # create even more errorneous diffs.
    # If this is the first message in the stream, this is going to fail, so we
    # can just pass on that iteration. Otherwise, the try statement should work.
    try:
        if t < buf[0]:
            continue
    except IndexError:
        pass

    # insort(x, y), which is from the bisect package, inserts sortable y into
    # iterable x in the correct location to keep the values in x ascending.
    insort(buf, t)

    # We require the following condition to spit out a delta: more than five
    # seconds elapsed between the most recent edit and the earliest edit. The
    # goal here is to create a kind of time-window. The difference of 5 seconds
    # between the highest and lowest time readings ensures that at least five
    # seconds have elapsed (on the server) since any event that would change the
    # diff that we are outputting. This roughly corresponds to the assumption
    # that the server will push out any changes within five seconds of it
    # happening. Note that this also works better than a fixed size window (e.g.
    # wait for at least 10 messages) in situations where the flow rate is low.
    if buf[-1] - buf[0] > 5:
        # Pop the first entry in the array (the oldest), removing it and
        # shifting everything over one spot.
        oldest = buf.pop(0)
        # Subtract it from the new first element (the second oldest)
        diff = buf[0] - oldest
        # dump the diff to stdout as a JSON with key 'delta'
        print(json.dumps({'delta': diff}))
        stdout.flush()
