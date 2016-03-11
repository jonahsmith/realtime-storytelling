# Jonah Smith
# util.py
# Assignment 3, Storytelling with Streaming Data, Spring 2016
#
# This script contains a series of functions that interact with the Redis
# database. They are used by several different components of this system. Note
# that they return Python objects, not JSON dumps, so that they can be used or
# repackaged by other Python programs as needed.

import redis
from collections import Counter
from math import log

# Establish the connection to the Redis table containing time diffs (used for
# rate)
rate_conn = redis.Redis(db=0)
# Establish the connection to the Redis table containing the distribution.
dist_conn = redis.Redis(db=1)


# This function generates the histogram as a JSON.
def histogram():
    # Get all the keys
    keys = dist_conn.keys()
    # .. and use them to get all of the entries.
    msgs = dist_conn.mget(keys)
    # Repeat these two steps until there are no None entries. Nones appear when
    # an entry expired between the time the list of keys was collected and the
    # time they were pulled from the db. This could slow things down, but I want
    # to make sure that we get a valid snapshot of the database at a particular
    # moment. Nones suggest that the histogram will not represent the
    # distribution because the distribution in the DB has changed.
    while not all(msgs):
        keys = dist_conn.keys()
        msgs = dist_conn.mget(keys)
    # Use counter to get a dictionary of counts for each entry (message).
    counts = Counter(msgs)
    # The number of messages is the denomentator for the proportion (e.g. we
    # need it to normalize below.)
    total = len(msgs)
    # Use a dictionary comprehension to generate a dictionary of the items and
    # their proportions in the total population.
    hist = {msg: count/float(total) for msg, count in counts.items()}
    return hist


# This function calculates the rate of the messages.
def rate():
    # Get the keys, and use those to retrieve all the diffs.
    keys = rate_conn.keys()
    diffs = rate_conn.mget(keys)
    # Again, we're going to repeat these two steps until there are no Nones.
    # Nones suggest that the collection of diffs has changed between getting
    # keys and retrieving entries, which means the results would be out of date.
    # Note, this would not work if it returned the actual integers because 0
    # evaluates to False. Luckily (or unfortunately, depending on your
    # perspective) Redis returns strings, so even '0' returns True. As such,
    # only Nones (or empty strings, which would be an error anyway) trigger a
    # recollection.
    while not all(diffs):
        keys = rate_conn.keys()
        diffs = rate_conn.mget(keys)
    # Convert all of the numbers from strings to floats. This will always work
    # because there are no Nones (because of the for loop above.) I'm using
    # float because it will make the division below later, and it is also
    # generalized, but for this data set everything in the DB is actually an
    # integer.
    diffs = [float(diff) for diff in diffs]
    # Now we just average all of the diffs in the database.
    avg = sum(diffs)/len(diffs)
    return avg


# This function calculates the entropy of the categorical distribution in the
# Redis db.
def entropy():
    # First, calculate the histogram.
    hist = histogram()
    # Now, our ugly entropy calculation. Inside, we have a list comprehension
    # that goes through each entry and calculate plog(p). Then we sum those, and
    # then negate the result..
    entropy = -sum( [p*log(p) for p in hist.values()] )
    return entropy


# This function calculates the probability of a particular message appearing in
# the stream, based on the categorical distribution in the Redis database.
def probability(msg):
    # First, get the histogram.
    hist = histogram()
    # Now, note that the entry is the probability. The calculation for the entry
    # in the histogram is the number of that message that has appeared, divided
    # by the total number of messages. That is the same calculation we would
    # have done to find the proportion of messages that are a certain kind. The
    # only wrinkle is that we have to return 0 (no probability) if that message
    # has not been observed before.
    prob = hist.get(msg, 0)
    return prob
