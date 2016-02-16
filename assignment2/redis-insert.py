from sys import stdin, stdout
from uuid import uuid1
import json
import redis

conn = redis.Redis()

while True:
    d = stdin.readline()
    diff = json.loads(d).get('delta')
    print(json.dumps({'delta': diff}))
    stdout.flush()
    conn.setex(str(uuid1()), diff, 120)
