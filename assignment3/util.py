import redis
from collections import Counter
from math import log

rate_conn = redis.Redis(db=0)
dist_conn = redis.Redis(db=1)


def histogram():
    keys = dist_conn.keys()
    articles = dist_conn.mget(keys)
    while not all(articles):
        keys = dist_conn.keys()
        articles = dist_conn.mget(keys)
    counts = Counter(articles)
    total = len(articles)
    hist = {article: count/float(total) for article, count in counts.items()}
    return hist


def rate():
    keys = rate_conn.keys()
    diffs = rate_conn.mget(keys)
    while not all(diffs):
        keys = rate_conn.keys()
        diffs = rate_conn.mget(keys)
    diffs = [float(diff) for diff in diffs]
    avg = sum(diffs)/len(diffs)
    return avg


def entropy():
    hist = histogram()
    entropy = -sum( [p*log(p) for p in hist.values()] )
    return entropy


def probability(title):
    hist = histogram()
    prob = hist.get(title, 0)
    return prob
