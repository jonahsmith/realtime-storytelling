# NYC AIR QUALITY STREAMER
# Jonah Smith
#
# This script polls a New York State government website for new air quality
# readings from a sensor at City College in uptown Manhattan every ten minutes.
# When there is a new reading, it is emitted to stdout as a JSON string. This
# can be viewed as is, or streamed over a websocket using a tool like
# websocketd. The measure for air quality is PM2.5, which is roughly the
# concentration of particles smaller than 2.5 micrograms (often called 'fine
# particles') in the air. More information about this measure can be found here:
# http://www.airnow.gov/index.cfm?action=aqibasics.particle
#
# The expected update frequency is about once per hour. The readings seem
# to be delayed by about an hour and fifteen minutes. For example, the reading
# for 10am becomes available around 11:15am. The documentation suggests that
# the data should be more or less realtime, so it is possible that the readings
# will be released more quickly in the future.
#
# source url: http://www.dec.ny.gov/airmon/getParameters.php?stationNo=73

from sys import stdout
from datetime import datetime, timedelta
import time
import requests

# last_update is used to decided whether the most recent reading from the server
# has already been seen and emitted by this script. We need to initialize a
# value when we start up, though, because the script has not yet seen any
# readings. 4 hours ago was an arbitrary choice, but based on a conceptual
# threshold: if the newest data are actually from further back than four hours
# ago, it's probably too old to be useful anyway.
last_update = datetime.now() - timedelta(hours=4)

# This loop will repeat indefinitely. It polls the data source, looks for a new
# reading, emits it if there is one, and then waits for 10 minutes.
# (Explanation for poll speed below.)
while True:
    curr_time = datetime.now()
    
    # start_time is used to cover an edge case, which is very early in the
    # morning (say, 12-2am). Usually we can just ask for today's readings, but
    # very early in the morning, the most recent reading may actually have been
    # the previous night. In this case, we want both yesterday's data and
    # today's data (if any). Early in the morning, subtracting 4 hours gives us
    # the previous day, so we will be requesting both yesterday's and today's
    # data, as desired. Note that if it's the middle of the day, the
    # start_time will be the same day as curr_time, so we will only get back
    # data for the current day, to reduce the size of the data response.
    start_time = curr_time - timedelta(hours=4)
    
    # This API call was uncovered by snooping around the source of the NYS air
    # sensor report request webpage:
    # http://www.dec.ny.gov/airmon/getParameters.php?stationNo=73
    base_url = 'http://www.dec.ny.gov/airmon/retrieveResults.php'
    payload = {
                # The 'channel' keys refer to which measurements to request. (I
                # am requesting everything.)
                'channel1': 'on',
                'channel5': 'on',
                'channel8': 'on',
                
                # `startDate` and `endDate` are the dates (in dd/mm/yyyy
                # format) we are interested in. As explained above, in the
                # middle of the day, these are equal. Early in the morning,
                # there may not be any readings for the current day, so we also
                # request the previous day.
                'startDate': start_time.strftime('%d/%m/%Y'),
                'endDate': curr_time.strftime('%d/%m/%Y'),
                
                # these do not seem to be user configurable, as experiments
                # returned blank data.
                'timebase': 60,
                'direction': 'back',
                'reports': 'CSV',
                
                # This is the ID for the sensor station we want. In this case,
                # we are interested in station 73, at City College.
                'stationNo': '73',
                
                # These does not seem to be user configurable.
                'numOfChannels': 8,
                'submitButton':'Create Report'
              }
    response = requests.get(base_url, params=payload)

    # The response is a CSV with a blank line at the end. So we split by
    # linebreaks (one list entry per observation) and select the second to last
    # one, which contains the most recent reading.
    latest_reading = response.text.split('\n')[-2]
    # Split the fields of that line. Note that this works because none of the
    # columns contain a comma.
    parsed_reading = latest_reading.split(',')
    # The date of the reading is in the first column, and the time is in the
    # second column. These columns have extra quotation marks, so we remove
    # them.
    latest_date = parsed_reading[0].replace('"', '')
    latest_time = parsed_reading[1].replace('"', '')
    # The fourth column (index 3 when we have 0 indexing) contains the P2.5
    # reading, one of the main ways to determine air quality.
    latest_p25 = parsed_reading[3]

    # We need to convert the datetime string to a datetime object in Python so
    # we can compare to this most recent reading with the last reading emitted
    # by this script. We concatenate the date and time strings with a space
    # between them, and we decode that string based on the observation that the
    # format is: YYYY-MM-DD HH:MM .
    last_sensor_update = datetime.strptime(latest_date + ' ' + latest_time, '%Y-%m-%d %H:%M')
    
    # If the last update to the dataset was more recent than the most recent
    # emitted data from this script, print out the JSON string and change
    # last_update to this datetime, as we have a new most recent update time.
    if last_sensor_update > last_update:
        print('{"p25": '+ latest_p25 + ', "update_time": "' + latest_date + ' ' + latest_time + '"}')
        # We need to flush stdout to make sure Python actually writes it to
        # stdout to be picked up by websocketd.
        stdout.flush()
        last_update = last_sensor_update

    # Pause for 10 minutes. We expect new readings every hour, but we want to
    # get new readings soon-ish without inundating the servers. This way, the
    # upper limit for how long we might go without seeing a new message is 10
    # minutes, a reasonable amount of time when we're talking in units of hours.
    time.sleep(60)
