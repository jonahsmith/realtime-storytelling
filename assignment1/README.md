---
name: Jonah Smith
uni: jes2258
date: February 10, 2016
course: Storytelling with Streaming Data
assignment: Assignment 1
---

# The data

One measure of air pollution is the concentration of 'fine particles,' defined to be less than 2.5 micrometers in diameter, in the air. These particles are emitted into the air by combustion of all sorts. They can have adverse effects on health and the environment, and the levels often change dramatically throughout the day, so there is value in tools that can present this information in real time.

Fine particle concentration is often measured in micrograms per cubic meter. This value measures how many micrograms of these small, less than 2.5 micrometer wide, particles we would we find if we were to sample 1 cubic meter of air.

Stations all around the world measure fine particle concentrations, and the data from many of them are freely available online.

I am collecting data from a fine particle sensor located at IS 143, a junior high school in Washington Heights, accessed through an API hosted by the [New York State Department of Environmental Conservation](http://www.dec.ny.gov/airmon/index.php). I selected this location because the sensor seems to be more reliable than others in Manhattan, and it is relatively near my apartment.

The New York State Department of Environmental Conservation [says](http://www.dec.ny.gov/airmon/index.php) that "in general, data is polled at the top of each hour from each station," and that "it is immediately displayed as it is collected." As such, we would expect the flow to be about one reading per hour. My experience is that new data are usually available about an hour and fifteen minutes after the polling time. For example, the 10am reading is usually available around 11:15am. I have occasionally found that the readings take longer than that to appear in the database, sometimes resulting in a rate lower than 1 reading per hour. (If at any point it seems like my data are not up to date, there is a good chance the sensor has not emitted a reading recently, so there has not been any new data for my script to collect. You can verify this by visiting the [sensor's webpage](http://www.dec.ny.gov/airmon/stationStatus.php?stationNo=56).)

My script polls the NYS Department of Environmental Conservation API for new readings from the IS 143 sensor every 10 minutes.  As I mentioned, the sensor devices themselves are only polled once per hour, so my script makes many more calls than necessary, and during most iterations does not find new readings or emit anything. The logic behind this frequency is that we will catch updates within 10 minutes of them being posted to the State database. This seems like a reasonable balance between wanting the data as soon as possible and recognizing that excessive requests to the API is inefficient for both the client and the host.

[According to New York State](http://www.dec.ny.gov/chemical/8541.html), all PM2.5 monitors on the site use one of two sensor models: the Rupprecht & Patashnick TEOM 1400ab, or the Rupprecht & Patashnick 2025 Partisol. They both seem to work essentially the same way. Air blows through a specially designed filter that traps fine particles. Using the volume of air that has blown through it and the increased weight of the filter, the sensors can then estimate the fine particle concentration at any given moment.

Each message in the stream, then, represents a measurement of the concentration of fine particles (less than 2.5 micrometers in diameter) in the air around the sensor (in this case, at IS 143 junior high school) at the moment the sensor was last polled.

One important thing to mention about these data is that they are the first-available measurements. While they are as real-time as it gets for this type of data, they have not been officially verified for accuracy.

# Included files
- `README.md`: you're looking at it! Includes a description of the data source (as per question 1 of the assignment), the included files, and how to run the program.
- `stream-air-quality.py`: a Python script to poll the sensor at IS 143 every 10 minutes. If a new reading has been added to the dataset since the last poll, that new reading is printed as a JSON string to stdout. (If there have been multiple updates, only the most recent is emitted.)
- `index.html`: This is a sample 'dashboard' type webpage that connects to a websocket (to be created by websocketd) and listens for new messages. For each new reading, it updates the last-updated time in the bottom left hand corner, changes the reading in the center circle, updates the safety level, and changes the background color accordingly. These are the levels:
	- PM2.5 <= 12: 'good' (green)
	- 12 < PM2.5 <= 35: 'moderate' (yellow)
	- 35 < PM2.5 <= 55: 'unhealthy for sensitive people' (orange)
	- PM2.5 > 55: 'unhealthy' (red)
As explained in the source comments for `index.html`, these cutoffs and colors come from [AirNow.gov's Concentration to Air Quality Calculator](http://www.airnow.gov/index.cfm?action=resources.conc_aqi_calc). I found the cutoffs manually, rather than directly computing the AQI. Reasoning can be found in the comments for that page.
- `test.py`: I recognize that the update rate is a bit slow for testing purposes (although within the acceptable range mentioned by Professor McGregor on Piazza). To help with the testing, I have included a small Python script that cycles through values within each of the ranges discussed above. It simply prints out a JSON string formatted identically to that emitted by `stream-air-quality.py`, but with one number from each range, pausing 5 seconds between emissions, and 10 seconds at the end of the cycle before repeating. This can be used to evaluate that the web page actually works within all of the ranges, and will work as the sensor is updated.

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