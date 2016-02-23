#!env/bin/sh

# Jonah Smith
# 2-notifications.sh
# Storytelling with Streaming Data, Spring 2016
#
# This is a convenience script that will launch the front-end of the
# notification system. It assumes that there is a redis server currently
# running, and that all of the entries contain a number of seconds between two
# subsequent events in the stream. When run, this script will generate Slackbot
# messages using the endpoint URL in CONFIG_SLACK.py.
#
# You'll need the following non-standard Python library to run it:
# - requests==2.9.1
#
# avg.py takes all of those redis entries, calculates the average, and dumps it
# out of stdout. This is our estimate for the beta parameter in an exponential
# distribution (e.g. the average amount of time between events).
# find-anomalies.py takes those averages from stdin and looks for anomalous
# values, based on the CDF of an exponential distribution with beta = 0.6 (what
# I have observed to be typical). When the value falls below the threshold, a
# JSON string is generated containing information about that event and output to
# stdout. That JSON string is read into slack.py, which loads the incoming
# messages url hook from CONFIG_SLACK.py and posts it to the Slack channel
# associated with it.

python avg.py | python find-anomalies.py | python slack.py
