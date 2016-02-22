# find-anomalies.py
# Jonah Smith
# Storytelling with Streaming Data, Spring 2016
#
# This script receives a stream of average time-between-messages (computed by
# avg.py from the redis database, which has all of the diffs from the previous
# 120 seconds) over stdin, and emits a JSON string to stdout if the average time
# between messages is lower than a certain value (discussed below). When the
# anomalous period ends (e.g. the average passes from below the threshold to
# above it), the program sends an 'ending' message, also as a JSON. There is
# also a rudimentary state management system to ensure that messages are only
# transmitted over stdout at the beginning and end of anomalous periods. This
# will continue indefinitely until the program is terminated. The bookending
# notifications are designed to help people keep track of when anomalous periods
# are happening and when they end. In addition to helping end users, the two
# notifications can also be used to analyze how long these anomalous periods
# tend to last.
#
# It relies on a threshold to consider something an anomaly. As explained in the
# README, the idea here is that Wikipedia reflects our changing knowledge,
# changing narratives about what is and is not knowledge, and the darker sides
# of human nature, like vandalism and online harrassment. For all of these, I am
# primarily interested in particularly busy moments, or moments of great change.
# As we discussed in class, stories require change, and a lot of edits on
# Wikipedia reflects a lot of change in the world. As such, we will only
# consider when we pass below a certain threshold (e.g. the average time between
# events has dropped to a small number, or the events are happening very
# frequently.)
#
# Now that we know we are interested in an lower bound, we need to decide what
# that bound should be. This can be done any number of ways, but one interesting
# way is to consider it probabilistically. The time between events in a Poisson
# process (which is often used for streams of data) is expressed as the
# exponential distribution. So, we can use an exponential distribution with
# parameter \beta = 0.6 (assuming time-between-event parameterization), and then
# we can find the value at which the probability drops below a certain
# threshold. Then, if the observation falls below that threshold, we call it an
# anomaly, because the probability of the paramter being 0.6 with that value is
# quite low (e.g. the probability of faster rates is higher.). Using
# [this](http://keisan.casio.com/exec/system/1180573222) calculator, it seems
# that values of 0.03 or lower will appear with probability < 0.05 if the
# underlying rate has not actually changed, so I will set this as the threshold.
# (0.05 is an arbitrary, though popular, choice, just based on an intuition that
# 5% chance is pretty small.) In other words, we are assuming the rate is 0.6,
# and if we start to see values of 0.03 seconds between messages or lower, it is
# highly unlikely that the underlying rate is still 0.6 (it is more likely to be
# lower, or more frequent, than that now.)

from sys import stdin, stdout
import json

# This is where we set our threshold. The process for deriving it is described
# in the comments above.
THRESHOLD = 0.03

# This is a variable that will keep track of whether the system is currently
# in an anomalous period or not. This is the main mechanism for preventing
# duplicate messages during a period of time with anomalous readings.
anomaly = False

while True:
    # Read in the input from stdin, which is a JSON with a key 'avg' containing
    # the average for the values in the DB (which have been there for < 120
    # seconds)
    line = stdin.readline()
    avg = json.loads(line).get('avg')
    
    # Now, if we find that the current average is less than the threshold,
    # we are experiencing anomalous behavior.
    if avg < THRESHOLD:
        # This is entered when the previous reading was not anomalous.
        if not anomaly:
            # Flip the anomaly boolean, so that next time we get this reading
            # we do not print out the message again.
            anomaly = True
            # Print out a JSON with the message. The JSON also includes the
            # rate and current time, which could be useful for the logging 
            # system.
            print(json.dumps({'message': 'An anomaly was detected.',
                  'rate': avg,
                  'timestamp': str(datetime.now()),
                 }))
            # As always, make sure to flush the stdout to prevent Python from
            # keeping a buffer.
            stdout.flush()
    # If the average reading is not anomalous...
    else:
        # This is entered only when the previous reading was anomalous. It
        # allows us to identify when an anomalous period has ended, and to
        # prevent us from sending messages when nothing is happening.
        if anomaly:
            # Swap the anomaly flag, so that if the next or a subsequent
            # reading is anomalous, it will be registered above.
            anomaly = False
            # Print a JSON string to stdout with the 'ended' message, the rate,
            # and the current timestamp.
            print(json.dumps({'message': 'The anomaly has ended.',
                              'rate': avg,
                              'timestamp': str(datetime.now()),
                             }))
            # Again, prevent Python from buffering the stdout.
            stdout.flush()
        
        