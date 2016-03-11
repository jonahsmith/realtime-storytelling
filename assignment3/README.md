---
title: Assignment 3
author: Jonah Smith (jes2258)
course: Storytelling with Streaming Data
---

# WikiWatcher 2

# The data

Perhaps unsurprisingly, the biggest Wikipedia language, by number of articles, is English. More surprisingly, though, the next is Swedish, a language with [9.2 million native speakers](https://en.wikipedia.org/wiki/Swedish_language), followed by Cebuano, a language from the Phillipines with [21 million native speakers](https://en.wikipedia.org/wiki/Cebuano_language). These languages have larger Wikipedias than much more common languages like Spanish ([470 million native speakers](https://en.wikipedia.org/wiki/Spanish_language)) or French ([80 million native speakers](https://en.wikipedia.org/wiki/French_language)).

But [the data](https://en.wikipedia.org/wiki/List_of_Wikipedias#Detailed_list) get stranger. Despite having a bit more than half as many articles as the English Wikipedia, the Swedish Wikipedia has less than 2 percent as many users. Cebuano Wikipedia has almost as many articles as Swedish Wikipedia, but only 5 percent the number of users. Clearly, something unusual is happening.

It turns out that many of the Swedish and Cebuano articles were written by [Lsjbot](https://en.wikipedia.org/wiki/Lsjbot), a project by a Swede who married a Filipino to create Swedish and Cebuano articles.

The point of this anecdote is that language Wikipedias resist simple summarization. Number of articles does not seem to be a good proxy for activity. We can learn many new things about the Wikipedia community by looking at the relative edit activity of different language Wikipedias. We might find when something significant is happening among a certain language community. More artistically, we could answer questions like 'does the sun ever set on the English Wikipedia empire?'

To look at this, I have connected to the Wikipedia edit feeds for the top thirtten Wikipedia language wikis by number of articles. (I have selected them because they have more than one million articles. This is an arbitrary milestone, but I wanted to capture the idea of what we would think of as a 'large' Wikipedia.) These categories are used as the basis of the histogram in my system.

Messages expire after fifteen minutes, but at least one representative for every observed category remains in the database indefinitely. This is because, if we have seen a message of a particular type, we know that it exists, which means we should always give it a non-zero probability. I picked fifteen minutes because it seems like a nice balance between gathering enough data to be representative (minutes, for example, seem too variable to have any particular meaning), but having a high enough resolution to adapt to real trends that are happening (for example, an article-writing bot like Lsjbot).

The threshold for the rate alerts (or rather, time-between-message alert) is 0.015. I selected it by capturing the typical rate (by casual sampling), which was about 0.27, using it as the parameter for an exponential distribution, and picking the 0.05 level, as in my second assignment. Again, 0.05 is not a magic number, but it captures the 'relatively unlikely' situation. If the average time-between-messages falls below this level, that suggests that there is a particularly large amount of activity, which would make it interesting for humans to investigate.

The probability threshold for alerts for unusual messages is [].

For entropy, I think we mainly be interested in situations where the distribution over the languages evens out. Certain languages (like English) generally dominate the stream, so there is pretty low entropy to begin with. As such, if a language like Cebuano, which based on my observation rarely gets edits, suddenly has a lot of edits, the entropy will rise because the distribution will even out. As such, we will set a threshold above which an entropy alert is triggered. I have observed that the entropy is often around []. 


# How it works

## Backend

Here is an overview of the structure of the backend:

```
            diff.py -> insert-diff.py
          /
ingest.py
          \
            insert-distribution.py
```

The backend system consumes the Wikipedia edit data stream (`ingest.py`) and sends it to two processes. The first (depicted as the top branch in this diagram) is used to calculate the rate. `diff.py` maintains a small queue and spits out time diffs between events in the stream. `insert-diff.py` takes those time diffs and sends them into the Redis database. (This system functions almost identically to that for Assignment 2.)

The bottom branch in this diagram (`insert-distribution.py` pulls out the variable in the stream whose distribution we are interested in capturing, and puts it into the Redis database. For values that have never been seen before, it inserts an entry for that value that does not have a time to live value, so that we never decrement the count for that value to 0. (Conceptually, we _know_ that it's possible for such a value to appear, even if it happens very infrequently, so we would not want it to disappear from the distribution entirely.)

## API

The API is in `api.py`. It has the following endpoints:

- `GET /histogram`
	- Retrieve the histogram, in JSON format. The keys are the category names, and the values are the ratios of total messages for that category to total messages of all categories.
- `GET /entropy`
	- Returns the entropy encoded as a JSON object.
- `GET /probability?message={}`
	- (Fill in {} with a URL encoded version of the message for which you are interested in the probability.)
	- Returns the probability of that message as a JSON object.

## Alerts

There are two parallel alert systems that are required to meet all the requirements for this assignment.

```
poll-stats.py -> find-anomalies.py -> slack.py

ingest.py -> find-unlikely.py -> slack.py
```

The first one is the evolution of the pervious alert system. Every second, `poll-stats.py` calculates the rate and the entropy and emits those. `find-anomalies.py` will use those messages to determine if they are anomalous, and if they are, they will emit the appropriate message over stdout to `slack.py`, which sends the messages to Slack.

The second listens connects to the stream coming from `ingest.py`, and then  `find-unlikely.py` calculates the probability of each message as it arrives. If it is below a certain threshold, it spits out a message that is sent by `slack.py`.

## Misc.

- `util.py` contains the procedures to calculate the histogram, the entropy, and the probability of a given message. (The same methods are needed in several modules, so I have put them in one central location and imported them in the modules that use them.)

# Run it

## Dependencies

Run `pip install -r requirements.txt` to install the Python requirements.

You also need Redis, and it should be running on the default port.

## Launching the backend

The backend will start loading things into the Redis database. To launch it, you can use the convenience script.

```
./1-backend.sh
```

Alternatively, you can use the following command.

```
python ingest.py | tee >(python diff.py | python insert-diffs.py) >(python insert-distribution.py)
```

This is launching an an instance of `ingest.py`, and splitting the output to both branches describedd above.

## Launching the API

Assuming the backend is already launched, you can start the API server by running the following command.

```
python api.py
```

You can then use a browser, cURL, or any other HTTP requesting mechanism to `localhost:5000` and the endpoints described above.

## Launching the alerts

Assuming the backend is already launched, the alerts can be launched all together using

```
./2-alerts.sh
```

_Note_: Ctrl-C is captured by this script and used to cut off the two alerting processes, which are run simultaneously. However, because of the way this is run, only the last process in the pipe gets killed. That means that the processes don't end until there's a cascade of failure caused by an unsuccessful attempt to push to that last process, which only takes place during alerts (which are infrequent). You may want to use `ps -A | grep python` to find the processes and kill them manually.

The alternative to launching this through the single shell command is to launch one or both of the following commands in shells.

```
python poll-stats.py | python find-anomalies.py | python slack.py

python ingest.py | python find-unlikely.py | python slack.py
```

## Showing the histogram

The histograms can be displayed by [].