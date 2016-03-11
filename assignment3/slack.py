# slack.py
# Jonah Smith
# Storytelling with Streaming Data, Spring 2016
#
# This script listens over stdin for anomaly JSON messages from
# find-anomalies.py, and then converts them into a message and broadcasts to a
# Slack channel. When an anomalous period begins, a message is sent with an
# alert and the current average rate. The time is also logged, so that the next
# time an anomalous period ends, the duration of that period is sent in the
# message.
#
# This could be hooked up to any Slack incoming webhook, if desired. The webhook
# URL used is in CONFIG_SLACK.py as a string assigned to the variable 'url.'

from sys import stdin, stdout, exit
import requests
import json
from datetime import datetime

# Here, we're going to import the `url` variable from the CONFIG_SLACK file,
# which should be in this directory. If we encounter issues importing, it's
# likely that it's because the user has not created the file or has not assigned
# the webhook url to the correct variable name (`url`) in that file. Let's spit
# out a nice warning to help people set it up correctly.
try:
    from CONFIG_SLACK import url
except ImportError:
    print('\nOops! You don\'t seem to have set up your Slack integration.\n'
          'Create a file in this directory called `CONFIG_SLACK.py`, and\n'
          'within it, make sure a variable called `url` is assigned to a\n'
          'string containing the webhook URL.\n')
    # Abort this Python process with exit code 1
    exit(1)

# Repeat this process indefinitely. This will look on stdin for new anomaly
# messages (signalling the beginning or end of an anomalous), and if there is
# one, it will send it to the Slack channel specified in CONFIG_SLACK.py.
while True:
    # Read the input from stdin, which will be JSON messages containing details
    # on the anomaly.
    line = stdin.readline()

    # As I mentioned, the stdin should be JSON strings, so we'll need to decode
    # it so we can access the keys.
    alert = json.loads(line)

    if alert.get('type') == 'rate_anomaly':
        # The 'anomaly' key is True if this is the beginning of an anomaly, and
        # 'false' if it is the end. So this 'if' statement runs at the beginning of
        # an anomalous period.
        if alert.get('anomaly'):
            # Log the time code from this message as the beginning of the anomalous
            # period. We'll use this later to estimate how long the anomalous
            # period lasted. We need to decode it, since when it is output in JSON
            # it is converted to a string with the following format:
            # YYYY-MM-DD HH:MM:SS.ffffff
            begin = datetime.strptime(alert.get('timestamp'), '%Y-%m-%d %H:%M:%S.%f')

            # Craft a string to be sent via Slack. It will contain the 'message' key
            # from the JSON string (which is free text), and it will mention the
            # average update speed that knocked it below the threshold.
            alert_text = ('Alert! {m} On average, edits are happening every '
                          '{t} seconds.').format(m=alert.get('message'),
                                                 t=round(float(alert.get('rate')), 2))

        # This code runs when the 'anomaly' key is False, which happens at the
        # end of anomalous periods.
        else:
            # Decode the time stamp of this alert message, as we did above.
            end = datetime.strptime(alert.get('timestamp'), '%Y-%m-%d %H:%M:%S.%f')
            # We can estimate the duration of the anomalous period by
            # subtracting the timestamp on this message from the timestamp on
            # the beginning of the anomalous period, captured by `begin`
            duration = (end - begin).total_seconds()
            # Let's round it to the nearest second. Less accurate, but we're not
            # dealing with exacts anyway, and it's unlikely the exact number is
            # as important as the order of magnitude.
            duration_est = int(round(duration))
            # Craft a string to be output through Slack, this time with just the
            # message and the approximate duration.
            alert_text = ('Alert! {m} That anomalous period lasted about '
                          '{d} seconds.').format(m=alert.get('message'),
                                                d=duration_est)

    # Same logic as above. If the type is high_entropy...
    elif alert.get('type') == 'high_entropy':
        # ... and it's the beginning of an anomaly, then we log the datetime
        # to a variable and spit out an alert.
        if alert.get('anomaly'):
            # Grabbing and decoding the timestamp.
            begin_ent= datetime.strptime(alert.get('timestamp'), '%Y-%m-%d %H:%M:%S.%f')
            alert_text = ('Alert! The entropy has gone above the threshold.'
                          ' Current entropy: {}').format(alert.get('entropy'))
        # Or if it's the end, we use the time to get a time diff between
        # beginning and end, and then we set the message to mention that.
        else:
            # Grabbing and decoding the timestamp, computing a diff, and then
            # setting up the message.
            end_ent = datetime.strptime(alert.get('timestamp'), '%Y-%m-%d %H:%M:%S.%f')
            duration_ent = (end_ent - begin_ent).total_seconds()
            duration_est_ent = int(round(duration_ent))
            alert_text = 'Alert! The entropy is back to normal. That lasted {} seconds.'.format(duration_est_ent)

    # The other type of message is 'unlikely message', which is to say that we
    # saw something we wouldn't have expected, based on the histogram. This
    # alert is simpler... just output the message as the alert.
    elif alert.get('type') == 'unlikely_message':
        alert_text = (u'Alert! An unlikely message, \'{}\', has appeared in '
                      'the stream!').format(alert.get('message'))

    # If we don't recognize the message type, don't do anything. This is to
    # avoid spamming the user with poorly formed messaged. The other option
    # might be to just dump the json as a string, but again, I want to keep the
    # user interaction as clean as possible.
    else:
        continue

    # The Slack API requires just this one argument, which is the content of
    # the message. We could build this out if we wanted, as detailed here:
    # https://api.slack.com/incoming-webhooks
    data = {'text': alert_text}

    # The Slack API specifies the data be encoded as a JSON string in the body
    # of the post request. This code accomplishes that. (The `json` parameter
    # will take a dictionary and post it as a JSON string, equivalent to:
    # data=json.dumps(data))
    r = requests.post(url, json=data)

    # Now we should check to make sure that the post went through. The status
    # code we are looking for is 200 (OK). If we don't get that, then we should
    # just fall back to printing to stdout.
    if r.status_code != 200:
        print('The following message failed to be delivered to Slack:\n' + alert_text + '\n')
        stdout.flush()
