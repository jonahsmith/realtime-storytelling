---
name: Jonah Smith
uni: jes2258
date: February 10, 2016
course: Storytelling with Streaming Data
assignment: Assignment 1
...

# The data

One measure of air pollution is the concentration of fine particles in the air. These particles are emitted into the air by combustion of all sorts, and can have adverse effects on health and the environment. There are stations set up around the world that take measurements of fine particle concentration.

'Fine particle' is a term used to describe, in particular, particles that are smaller than 2.5 micrometers in diameter. All of the stations I have looked at release data about the concentration measured in micrograms per cubic meter. In other words, if we took a cubic meter of outside air, how many micrograms of these small, less than 2.5 micrometer wide, particles would we find in it?

I am collecting data from the [New York State Department of Environmental Conservation](http://www.dec.ny.gov/airmon/index.php). They [claim](http://www.dec.ny.gov/airmon/index.php) that "in general, data is polled at the top of each hour from each station," and that "it is immediately displayed as it is collected." As such, we would expect the flow to be about one reading per hour. My experience with these data is that new data are available about an hour and fifteen minutes after the polling time. For, the 10am reading is available around 11:15am. I have occasionally found that the readings take longer than that to appear, sometimes resulting in a rate lower than 1 reading per hour. The absolute latest data are available on the [sensor's webpage](http://www.dec.ny.gov/airmon/stationStatus.php?stationNo=73).

My script, which collects data from an API hosted by the New York State Department of Environmental Conservation, polls for new readings every 10 minutes. Again, the sensor devices themselves are only polled once per hour, so my script makes many more calls than necessary, and during most iterations does not emit anything. The logic behind polling the API every 10 minutes is that we will catch updates within 10 minutes of them being posted to the State database. This seems like a reasonable balance between wanting the data as soon as possible and recognizing that excessively requesting new data from the API is inefficient for both the client and the host.

[According to New York State](http://www.dec.ny.gov/chemical/8541.html), all PM2.5 monitors on the site use one of two sensor models: the Rupprecht & Patashnick TEOM 1400ab, or the Rupprecht & Patashnick 2025 Partisol. Both of these devices seem to work essentially the same way. Air blows through a specially designed filter that traps fine particles. Using the volume of air that has blown through it and the increased weight of the filter, the sensors can then estimate the fine particle concentration at any given moment.

Each message in the stream, then, represents the concentration of fine particles in the air around the sensor at the moment the sensor was polled.

One important thing to mention about these data is that they are the first-available measurements. While they are as real-time as it gets for this type of data, they have not been verified for accuracy.

# Included files
- `README.md`: you're looking at it! Includes a description of the data source (as per question 1 of the assignment), the included files, and how to run the program.
- `stream-air-quality.py`: a Python script to poll the sensor at City College every 10 minutes. If a new reading has been added to the dataset since the last poll, that new reading is printed as a JSON string to stdout. (If there have been multiple updates, only the most recent is emitted.)
- `index.html`: This is a sample 'dashboard' type webpage that connects to a websocket (to be created by websocketd) and listens for new messages. For each new reading, it updates the last-updated time in the bottom left hand corner, changes the reading in the center circle, updates the safety level, and changes the background color accordingly. These are the levels:
	- PM2.5 <= 12: 'good' (green)
	- 12 < PM2.5 <= 35: 'moderate' (yellow)
	- 35 < PM2.5 <= 55: 'unhealthy for sensitive people' (orange)
	- PM2.5 > 55: 'unhealthy' (red)
As explained in the source comments for `index.html`, these cutoffs and colors come from [AirNow.gov's Concentration to Air Quality Calculator](http://www.airnow.gov/index.cfm?action=resources.conc_aqi_calc). I found the cutoffs manually, rather than directly computing the AQI. Reasoning can be found in the comments.
- `test.py`: I recognize that the update rate is a bit slow for testing purposes (although within the acceptable range mentioned by Professor McGregor on Piazza). To help with the testing, I have included a small Python script that cycles through values within each of the ranges discussed above. It simply prints out a JSON string formatted identically to that emitted by `stream-air-quality.py`, but with one number from each range, pausing 5 seconds between emissions, and 10 seconds at the end of the cycle before repeating. This can be used to evaluate that it actually works at all of ranges, and will work as the sensor is updated.

# How to run

## Dependencies
- For Python, the only dependency is `requests`
- To use the webpage, you will need [`websocketd`](http://websocketd.com/)

## Print incoming data to stdout

To print the data to stdout (e.g. part 2 of the assignment), simply run

```
python stream-air-quality.py
```

## Live web page

To see live data on the webpage I have created (e.g. part 3 of the assignment), run

```
websocketd --port 8080 python stream-air-quality.py
```

and then open `index.html` in Chrome. There is no need to use a formal web server for the HTML page because it has no dependencies. If you would like, however, you can run:

```
python -m SimpleHTTPServer
```

from within the project directory, and then open a web browser to `http://localhost:8000`.

## Test the web page

You can test the webpage (run through sample values for the air quality) using the same steps as above in 'Live web page,' but substitute `test.py` for `stream-air-quality.py` above, e.g.

```
websocketd --port 8080 python test.py
```

Then open the HTML page as before.