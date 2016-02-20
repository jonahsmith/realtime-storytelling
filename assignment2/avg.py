# avg.py
# Jonah Smith
# Storytelling with Streaming Data, Spring 2016
#
# This script periodically takes the average of all of the values in a Redis
# database. In principle, these values could be anything, but it was designed
# to be used with the flow rate scripts, which contain time diffs between
# consecutive Wikipedia edits in seconds. These entries are set to expire every
# 120 seconds. These averages create another stream, which are transmitted
# through stdout.

from redis import Redis
import json
from sys import stdout
from time import sleep

# Connect to the redis db server over the default port (6379). Note that the
# redis server process needs to be running already! In fact, it should be
# running, and there should be another process stuffing time diffs into it.
db = Redis()

# Repeat the averaging indefinitely. 
while True:
    # First, grab all the keys from the db
    keys = db.keys('*')

    # Now, grab all of the entries for those keys
    entries = db.mget(keys)

    # Values come out of the Redis database as strings, but we want to compute
    # the average, so we'll need to turn them into floats. Note that in the
    # motivating example of Wikipedia edits, the time diffs are actually ints.
    # I'm converting to floats because it will make the eventual division a bit
    # simpler (since integer division in Python produces an integer, whereas
    # we want fractional seconds for our average flow rate), and it also
    # generalizes to cases when the time diffs are fractional to begin with.
    #
    # Note that this is going to fail occasionally because we are pulling keys,
    # and then we are retrieving all the entries later. The time between these
    # two events may be enough for some of the entries to expire and be removed
    # from the database. In that case, we get an array with mostly numbers,
    # but also at least one None. We have two options: ignore the entries that
    # disappeared prematurely (e.g. [float(t) for t in test if t is not None]),
    # or skip the iteration. I have decided to skip the iteration because I
    # think it is more accurate. Simply not including that value returns a
    # different result than _either_ if the entry hadn't disappeared
    # prematurely, or if you recollected keys and entries. As such, other than
    # maintaining a steady flow of averages (which is not necessary in this
    # situation), it is hard to justify ignoring the None entries. The side
    # effect is that if the Redis db is accidentally being used for something
    # else (that is not using number values), it will prevent us from
    # calculating averages that are not what we intended.
    try:
        time_diffs = [float(entry) for entry in entries]
    # Only accept TypeError, which is what happens when None appears
    except TypeError:
        continue

    # Compute the average of all of the time diffs that had been in the
    # database. This corresponds to 'the average time between two events in
    # the stream.'
    avg = sum(time_diffs)/len(time_diffs)

    # Print that average to stdout, as a JSON string with a single key: avg.
    print(json.dumps( {'avg': avg } ))

    # Make sure to flush stdout, so that we don't end up with Python's buffer.
    stdout.flush()

    # Rest for 1 second before repeating the process.
    sleep(1)
