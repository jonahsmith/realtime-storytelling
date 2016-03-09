# redis-insert.py
# Jonah Smith
# Assignment 3, Storytelling with Streaming Data, Spring 2016
#
# (Some of this code originally appeared in my submission for Assignment 2)
#
# This script takes the Unix-piped stream from diff.py (which are time deltas)
# between events in the stream and adds it to redis with a unique identifier.
#
# Although I wrote it independently, the idea is based on:
# https://github.com/mikedewar/RealTimeStorytelling/blob/master/2/insert.py

from sys import stdin, stdout
from uuid import uuid1
import json
import redis

# Connect to the diff redis db
conn = redis.Redis(db=0)

while 1:
    # This is the piped time deltas from diff.py
    d = stdin.readline()
    # The time diff is in the key 'delta'
    diff = json.loads(d).get('delta')

    # Add it to the database; have it expire after 120 seconds (2 mins). This
    # 'expiration' time makes a big impact on the smoothness of the function we
    # get. I found after some experimentation that 120 seconds yields a nice and
    # smooth function that still has variability.
    conn.setex(str(uuid1()), diff, 120)

    # Print to stdout as a confirmation--this doesn't do anything functional.
    print(json.dumps({'delta': diff}))
    stdout.flush()
