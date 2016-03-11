#!/usr/bin/env bash
#
# Jonah Smith
# 2-alerts.sh
# Assignment 3, Storytelling with Streaming Data, Spring 2016
#
# This convience script launches both alerting systems. The first command polls
# the rate and entropy of the database every one second, then outputs it to the
# anomaly detector, and any anomalies that are found are sent via Slack. The
# second command listens to the stream, and for each message, calculates the
# probability of the incoming messages using the data in the Redis database as
# the reference distribution.

# This command sets up alerts for entropy and rate anomalies.
python poll-stats.py | python find-anomalies.py | python slack.py & PID0=$!
# This command sets up alerts for unlikely messages (articles) in the stream.
python ingest.py | python find-unlikely.py | python slack.py & PID1=$!

cleanup() {
  kill $PID0
  kill $PID1
}

ctl_c() {
  echo "Killing the alert processes..."
  echo "(You may also want to `ps -A | grep python` to make sure everything was cleaned up.)"
  cleanup
  exit 0
}

trap ctl_c SIGINT

while true; do read x; done
