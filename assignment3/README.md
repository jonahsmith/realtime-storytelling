---
title: Assignment 3
author: Jonah Smith (jes2258)
course: Storytelling with Streaming Data
---

# WikiWatcher 2

# The data

Perhaps unsurprisingly, the biggest Wikipedia language, by number of articles, is English. More surprisingly, though, the next is Swedish, a language with [9.2 million native speakers](https://en.wikipedia.org/wiki/Swedish_language), followed by Cebuano, a language from the Philippines with [21 million native speakers](https://en.wikipedia.org/wiki/Cebuano_language). These languages have larger Wikipedias than much more common languages like Spanish ([470 million native speakers](https://en.wikipedia.org/wiki/Spanish_language)) or French ([80 million native speakers](https://en.wikipedia.org/wiki/French_language)).

But [the data](https://en.wikipedia.org/wiki/List_of_Wikipedias#Detailed_list) get stranger. Despite having a bit more than half as many articles as the English Wikipedia, the Swedish Wikipedia has less than 2 percent as many users. Cebuano Wikipedia has almost as many articles as Swedish Wikipedia, but only 5 percent the number of users. Clearly, something unusual is happening.

As it turns out that many of the Swedish and Cebuano articles were written by [Lsjbot](https://en.wikipedia.org/wiki/Lsjbot), a project by Sverker Johansson, a Swede who is married to a Filipino, that creates Swedish and Cebuano articles.

The point of this anecdote is that language Wikipedias resist simple summarization. Number of articles does not seem to be a good proxy for activity levels. We can learn many new things about the Wikipedia community by looking at the relative edit activity of different language Wikipedias. We might find when something significant is happening among a certain language community. More artistically, we could answer questions like 'does the sun ever set on the English Wikipedia empire?', or we might be able to see sleep patterns for certain parts of the world.

To look at this, I have connected to the Wikipedia edit feeds for the top thirteen Wikipedia language wikis by number of articles. I selected those thirteen because they are the only Wikipedias with more than one million articles. This is an arbitrary milestone, but I wanted to capture the idea of what we would think of as a 'large' Wikipedia. These categories are used as the basis of the histogram in my system.

Messages expire after fifteen minutes, but one representative for every observed category remains in the database indefinitely. This is because, if we have seen a message of a particular type, we know that it exists, which means we should always give it a non-zero probability. I picked fifteen minutes because it seems like a nice balance between gathering enough data to be representative (a minute, for example, seems like it would be too variable to have any particular meaning), but having a high enough resolution to adapt reasonably quickly to real trends that are happening (for example, an article-writing spree by a bot like Lsjbot).

The threshold for the rate alerts (or rather, time-between-message alert) is 0.015. I selected it by casually sampling the typical rate, which was about 0.27, using that rate as the parameter for an exponential distribution, and picking approximately the 0.05 level, as in my second assignment. Again, 0.05 is not a magic number, but it captures the goal of 'relatively unlikely' false-positives situation, where we would expect to observe it by chance very rarely under an exponential distribution with parameter 0.27. If the average time-between-messages falls below this level, that suggests that there is a particularly large amount of activity, which would make it interesting for humans to investigate.

The probability threshold for alerts for unusual messages is 0.05, again mimicking the 0.05 level that is popular for p-values. I also picked it based on the context. Ultimately, what this will do is trigger alerts when an edit arrives in a language that makes up less than 5 percent of the edit stream. In other words, we'll get alerts when edits are made to articles for languages where edits are not often made. I would personally be interested in seeing such alerts, just to see what types of changes were made and to what article. At the 10 percent level, I think we would get too many alerts, as languages making up less than 10 percent of the stream are still relatively frequent. The 5 percent level, on the other hand, seems infrequent enough to only get interesting edits, but frequent enough that it would actually get triggered. In practice, as with any other threshold, someone running this might prefer to change it based on whether he or she is getting too many or not enough notifications.

For entropy, my feeling is that we are mainly interested in situations where the distribution over the languages evens out. Certain languages (like English) generally dominate the stream, so there is pretty low entropy to begin with. As such, if a language like Cebuano, which based on my observation rarely gets edits, suddenly has a lot of edits, the entropy will rise because the distribution will even out. As such, we will set a threshold above which an entropy alert is triggered. I have observed that the entropy is often around 1.7. With thirteen categories, the maximum entropy is `-(13*(1/13)*log(1/13)) = log(13) = 2.565`. As a first pass, we can say that we should trigger an alert if we're halfway to the perfect entropy scenario from the typical scenario. That happens at `1.7 + (2.565 - 1.7)/2 = 2.133`. Rounding, we will set the threshold to 2.1. In practice, we might adjust this depending on whether we feel like the frequency it yields is at a desirable level. (We would raise it if we're getting too many alerts, or lower it if we're not getting enough.)

As with my last assignment, alerts are sent through Slack, as it seems like Slack is quickly becoming an important part of many office environments. Note, if I provided this repository

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

The backend system consumes the Wikipedia edit data stream (`ingest.py`) and sends it to two processes. The first (depicted as the top branch in this diagram) is used to calculate the rate. `diff.py` maintains a small queue (to reorder messages that arrive out of order) and spits out time diffs between events in the stream. `insert-diff.py` takes those time diffs and sends them into the Redis database. (This system functions almost identically to that for Assignment 2.)

The bottom branch in this diagram (`insert-distribution.py`) pulls out the variable in the stream whose distribution we are interested in capturing ('wiki,' which is unique to each language), and puts it into the Redis database. For values that have never been seen before, it inserts an entry for that value that does not have a time to live value, so that we never decrement the count for that category to 0. (Conceptually, we _know_ that it's possible for such a value to appear, even if it happens very infrequently, so we would not want it to disappear from the distribution entirely.)

## API and visualization

The API is in `api.py`. It has the following endpoints:

- `GET /histogram`
	- Retrieve the histogram, in JSON format. The keys are the category names, and the values are the ratios of total messages for that category to total messages for all categories.
- `GET /entropy`
	- Returns the entropy encoded as a JSON object.
- `GET /probability?message={}`
	- (Fill in {} with a URL encoded version of the message for which you are interested in the probability.)
	- Returns the probability of that message as a JSON object.
- `GET /vis` (use a browser)
	- View the webpage with a simple visualization of the distribution over the languages. Note that this does not update by itself; to update the distribution, reload the page. 

## Alerts

There are two parallel alert systems that are required to meet all the requirements for this assignment.

```
poll-stats.py -> find-anomalies.py -> slack.py

ingest.py -> find-unlikely.py -> slack.py
```

The first one is the evolution of the previous alert system. Every second, `poll-stats.py` calculates the rate and the entropy and emits those. `find-anomalies.py` will use those messages to determine if they are anomalous, and if they are, they will emit the appropriate message over stdout to `slack.py`, which sends the messages to Slack. NOTE: before you can use `slack.py`, you must create a file called `CONFIG_SLACK.py`, which contains the endpoint URL for your Slack channel in the following format:

```
url = 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
```

The second command connects to the stream coming from `ingest.py`. `find-unlikely.py` then calculates the probability of each message as it arrives. If it is below a certain threshold, it spits out a message that is sent by `slack.py`.

## Misc.

- `util.py` contains the procedures to calculate the histogram, the entropy, and the probability of a given message. (The same methods are needed in several modules, so I have put them in one central location and imported them in the modules that use them.)

# Run it

## Dependencies

Run `pip install -r requirements.txt` to install the Python requirements.

You also need [Redis](http://redis.io/), and it should be running on the default port.

Finally, you'll need to have a Slack channel set up and ready for a Slackbot. If I have provided this code (e.g. you're not accessing this through the GitHub repo), this is already set, although you'll want to log into the Slack team to check out the notifications it produces. The team is called jonahssandbox and I think you will be able to sign up if you have an @columbia.edu email address. If this doesn't work, please contact me and I can set you up.

## Launching the backend

The backend will start loading the time diffs between messages and the distribution of languages into the Redis database. To launch it, you can use the convenience script.

```
./1-backend.sh
```

Alternatively, you can use the following command.

```
python ingest.py | tee >(python diff.py | python insert-diffs.py) >(python insert-distribution.py)
```

This is launching an instance of `ingest.py`, and splitting the output to both branches described above.

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

_Note_: Ctrl-C is captured by this script and used to cut off the two alerting processes, which are run simultaneously. However, because of the way this is run, only the last process in the pipe gets killed. That means that not all processes are killed immediately; you must wait until there's a cascade of pipe failures caused by an unsuccessful attempt to push to that last process, which only takes place during alerts (which are relatively infrequent). You may want to use `ps -A | grep python` to find the processes and kill them manually.

The alternative to launching this through the single shell command is to launch one or both of the following commands in shells. The first does alerts for rate and entropy. The second does alerts for unlikely messages.

```
python poll-stats.py | python find-anomalies.py | python slack.py

python ingest.py | python find-unlikely.py | python slack.py
```

## Showing the histogram

The histogram can be viewed by launching

```
python api.py
```

Then, open a web browser and visit localhost:5000/vis . Note that this does not reload on its own; rather you should refresh the page to get the updated data.