# insert-distribution.py
# Jonah Smith
# Assignment 3, Storytelling with Streaming Data, Spring 2016
#
# This script takes a pipe from stdin, in which every message is a JSON
# corresponding to a single edit on english Wikipedia. It extracts the city name
# and puts that into a Redis database (running on the default port) as the
# value of an entry. (The key is a randomly generated unique identifier.)
#
# Entries are set to expire after 15 minutes. This time seems like a good scale
# for Wikipedia edits, because minute-to-minute there might be too much noise to
# get a good sense of the distribution, but anything longer than about half an
# hour would fail to capture the variations we are interested in (like a bot or
# a burst of activity in response to some major event), which could happen at a
# scale less than fifteen minutes. Fifteen minutes allows us to observe some
# variation without being a slave to random noise.

import redis
from sys import stdin
import json
from uuid import uuid1


# Establish a Redis connection on the default port, but with db index 1. This
# will allow us to separate the distribution database from the database
# containing time diffs (which is used to calculate the rate).
conn = redis.Redis(db=1)

# This variable is going to hold all of the categories we have seen before.
# That's important so that we can put one entry in the DB that will never erase
# (since we know there is always a non-zero probability of that category
# existing).
seen = set([])

# Repeat indefinitely...
while 1:
    # Read the JSON string from stdin, and load it into a Python dictionary.
    nextline = stdin.readline()
    edit = json.loads(nextline)

    # Grab the type of the change.
    change = edit.get('wiki')

    # If we've seen this entry before, put a normal entry that will expire. When
    # it expires, there will still be at least one entry in the DB of that
    # category.
    if change in seen:
        # Add the article name to our database with a unique identifier key. Set
        # the expiration time to 15 minutes (see above for a discussion.)
        conn.setex(str(uuid1()), change, 900)
    # If we have not seen this category before, we need to add a permanent entry
    # in Redis so that we always give it a non-zero probability of happening,
    # regardless of how long it has been since the last one. Also, add it to our
    # set of seen categories so we don't add another permanent entry.
    else:
        seen.add(change)
        conn.set(str(uuid1()), change)
