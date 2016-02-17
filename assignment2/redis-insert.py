# redis-insert.py
# Jonah Smith
# Storytelling with Streaming Data, Spring 2016
#
# This script takes the Unix-piped stream from diff.py (which are time deltas)
# and adds it to redis with a unique identifier.

from sys import stdin, stdout
from uuid import uuid1
import json
import redis

# Connect to the redis db
conn = redis.Redis()

while True:
    # This is the piped time deltas from diff.py
    d = stdin.readline()
    # The value is in the key 'delta'
    diff = json.loads(d).get('delta')
    
    # Add it to the database; have it expire after 2 mins.
    conn.setex(str(uuid1()), diff, 120)

    # Print to the command line as a confirmation--this doesn't do anything
    # functional.
    print(json.dumps({'delta': diff}))
    stdout.flush()
