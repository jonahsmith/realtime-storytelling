# insert-distribution.py
# Jonah Smith
# Assignment 3, Storytelling with Streaming Data, Spring 2016
#
# This script takes a pipe from stdin, in which every message is a JSON
# corresponding to a single edit on english Wikipedia. It extracts the city name
# and puts that into a Redis database (running on the default port) as the
# value of an entry. (The key is a randomly generated unique identifier.)

# Entries are set to expire after []. This is because [].

import redis
from sys import stdin
import json
from uuid import uuid1


# Establish a Redis connection on the default port, but with db index 1. This
# will allow us to separate the distribution database from the database
# containing time diffs (which is used to calculate the rate).
conn = redis.Redis(db=1)

# Repeat indefinitely...
while 1:
    # Read the JSON string from stdin, and load it into a Python dictionary.
    nextline = stdin.readline()
    edit = json.loads(nextline)

    # Grab the title of the article. These are unique to each article, so we
    # will use these values later to form our distribution of edit events over
    # articles in english Wikipedia.
    article = edit.get('title')

    # Add the article name to our database with a unique identifier key. Set
    # the expiration time to [] (see above for a discussion.)
    conn.setex(str(uuid1()), article, 3600)
