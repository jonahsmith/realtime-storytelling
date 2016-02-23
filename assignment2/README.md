---
name: Jonah Smith
uni: jes2258
date: February 24, 2016
course: Storytelling with Streaming Data
assignment: Assignment 2
---

![screenshot](img/slack-screenshot.png 'A screenshot of the Slackbot. Note: the rate shown in this screenshot is not the actual rate that will trigger notifications. I modified the threshold so that I could trigger an event to show it working.')

# Overview

This repository contains a collection of scripts that, when used together, alerts the user via Slack when the Wikipedia edit rate is unusually high. The details of implementation are discussed below and within scripts as comments.

(Please note that because my [last project](https://github.com/jonahsmith/realtime-storytelling/tree/master/assignment1) used a stream with an update rate fixed at once per hour, I have decided to change data streams for this project.)

# The data

Wikipedia has become a widely used and important source of information. It is also unique in that the articles are written collaboratively by contributors all around the world.

There is a feeling, perhaps overstated, that monitoring changes on Wikipedia is like watching history or human discovery happen in real time. At the very least, these changes reflect changes in the narratives we construct about ourselves and the world around us, about what we know and do not know, about what is important and what is not. And, of course, these changes also reflect the darker elements of human behavior, including the impulses towards vandalism and harassment.

The ebb and flow of changes in this important store of collective knowledge has been the subject of interpretation for storytellers of all sorts, ranging from [musicians](http://listen.hatnote.com/) to [journalists](http://observer.com/2016/01/donald-trumps-wikipedia-page-is-the-busiest-of-the-cadidates/).

Wikipedia makes edits available live to the public via several methods, including an [IRC feed](https://meta.wikimedia.org/wiki/Research:Data#IRC_Feeds) and a [websocket](https://wikitech.wikimedia.org/wiki/RCStream) using the [socket.io protocol](http://socket.io/). This project connects to the websocket feed.

Messages sent through these feeds represent a single submission of edits to the content of a single page on Wikipedia. An individual can make as many changes to a page as he or she desires, and then submit those changes together, and they are immediately reflected on the page, though many are quickly reverted because they did not meet Wikipedia standards. These submissions are the events. The messages contain several pieces of metadata, including what page was changed, the before and after sizes of the article (in bits), and a timestamp for the change. I have chosen to subset the events to only those that reflect changes to articles, as opposed to, for example, the media associated with pages, because I believe this subset is what is most interesting from a storytelling perspective: changes to actual textual content. I have also limited this to Wikipedia in English, simply because it is the language I speak, and also seems to be one of the more active.

My experience, based on monitoring at several different days and times, is that the update rate is around 1.7 messages per second, or roughly 0.6 seconds between messages, but an exciting aspect of this stream is that the update rate is somewhat unpredictable. The variation, in fact, is what this project is set up to explore.

This particular project makes alerts if the edit rate speeds up. My idea is that one would be interested in especially busy times on Wikipedia, as these represent moments might reflect big changes in the world, or our perception of it, and these could be the source of potentially important and interesting stories.

To that end, I have selected a threshold for the average time-between-messages below which a notification is sent out. This threshold is based on an exponential distribution, which can be used to represent the time between events in a Poisson process. If the true underlying rate is 0.6 seconds between messages, then the probability of seeing 0.03 seconds or lower between messages by chance is less than 0.05, so I have set this as the threshold. (Put another way, if the average goes below this value, the probability that the underlying rate is still 0.6 is quite low, it is probably lower/faster.) 0.05 was an arbitrary choice based on the commonly used—and maligned—p-value, which itself is based on the intuition that 5% is a pretty low chance. Thus, I have tried to ground my storytelling idea (the rate of change increasing says something about the world) in some probabilistic reasoning. (The particular value was computed using the left-tail probability using [this site](http://keisan.casio.com/exec/system/1180573222), which conveniently happens to use the beta parameterization of the exponential distribution.)

The notifications are transmitted over Slack. (The repository on GitHub does not contain the URL to post on Slack, but if I provided this code to you directly, it is available on [this Slack team](jonahssandbox.slack.com).) One notification is sent at the beginning of an 'anomalous period' (when the value first dips below the threshold) and at the end (when the value first goes back into the normal range after being below the threshold for any amount of time). Bookending notifications are used because I think it is helpful to be able to tell, based on the notifications, whether a period of anonamalous activity has concluded or not. (This was partially based on my frustration with an app I have on my phone that notifies you of subway delays, but does not notify you when normal service is restored.) This design can also help track how long anomalous periods tend to last, which could be another interesting statistic.

# Included files

This program consists of a backend and a frontend.

The backend is responsible for connecting to the Wikipedia edit stream, calculating the amount of time that elapsed between two events, and loading these time differences into a Redis in-memory database.

The frontend of this system is responsible for calculating the average amount of time between consecutive events (using the data in the Redis database), creating an alert when the average time-between-consecutive-events falls below 0.03 seconds, and communicating these anomalies to humans via Slack.

## Backend

- `1-stream-ingest.sh`
	- A convenience shell script to launch the entire backend in one command. Before running this, make sure there is a Redis database server serving over the default port (6379)!
- `ingest.py`
	- This script connects to the Wikipedia edit stream websocket, and outputs the edit event messages to stdout.
- `diff.py`
	- This script reads the event messages via stdin, retrieves the timestamp (Unix epoch time) and then calculates the elapsed (server) time between two events and outputs them to stdout. Worth mentioning: this script implements a very simple buffer to resolve issues with receiving events out of order through the stream. The implementation details are outlined in the code, but as an overview, this code ensures that at least 5 seconds have elapsed on the server since the oldest message before calculating a time difference. (5 seconds is a balance between having minimal delay and not wanting to miss messages. I have found that this time very rarely misses messages and adds acceptable delay to the stream.) Messages that still arrive after they should have been processed are discarded, so as not to create a cascade of mistakes.
- `redis-insert.py`
	- This script takes the time differences and sticks them into a Redis database, each with a 120 second lifespan. I messed around with different time increments and found that 120 seconds was a nice balance of smoothness and variability.

## Frontend

- `2-notifications.sh`
	- A convience script to launch the entire frontend at once. It is assumed that you have run already run `1-stream-ingest.sh` and waited a few minutes (perhaps about two and a half minutes), so that the Redis database has had time to be populated. This script will not fail if you have not done this, but it may give wildly varying results for the first several seconds because of the small sample size in the Redis database.
- `avg.py`
	- This script looks at all entries in the Redis database and calculates the average of the time differences there. It outputs this average to stdout.
- `find-anomalies.py`
	- This script reads the average values coming via stdin from `avg.py` and checks if the value is consistent with anomalous behavior. The method for defining 'anomalous' is mentioned above and in the code. This emits one JSON string at the beginning of an anomalous period (e.g. when the edit rate passes a certain threshold), and then emits another one at the end of that anomalous period (e.g. when the edit rate passes back into the normal range from the anomalous range). Note that the threshold should happen quite rarely. (Testing tips are below, in the section 'How to Run'.)
- `slack.py`
	- This script reads the anomaly data from stdin and creates a message to be posted on Slack. It then posts that message to the Slack channel using the URL in `CONFIG_SLACK.py`.
- [`CONFIG_SLACK.py`]
	- This file is not included, unless I've sent you the repository directly (e.g. not via GitHub). You must create it yourself, or use the repository I have provided! It should contain a single line, which should look like `url = '[someurl]'`, where someurl is your Slackbot's URL. It should look something like `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX`.

# How to Run

## Dependencies and other requirements

Please use pip for some other Python package manager to install the following non-standard packages:

- `socketIO_client==0.5.6`
- `redis==2.10.5`
- `requests==2.9.1`

Also, you should have the Redis in-memory database system installed on your machine, and the server should be running on the default port when you try to run this. If you don't have it installed yet, you can do so using brew:

```
brew install redis
```

Then to start the server:

```
redis-server
```

Finally, you'll need to have a Slack channel set up and ready for a Slackbot. If I have provided this code (e.g. you're not accessing this through the GitHub repo), this is already set, although you'll want to log into the Slack team to check out the notifications it produces. The URL is [jonahssandbox.slack.com](jonahssandbox.slack.com) and I _think_ you will be able to sign up if you have an @columbia.edu email address. If this doesn't work, please contact me and I can set you up.

**If you are reading this directly from the GitHub repo, or you want to set up the notifications to appear on a different Slack channel, you must follow these directions.**

The details of this may change, so I don't want to be too detailed with the instructions here, but in general you can go to [Slack's API webpage](https://api.slack.com/), log in, click the button that says 'Start building custom integrations,' and follow the instructions to setup an 'Incoming Webhook.' Once that URL is set, you must insert that URL into a file called `CONFIG_SLACK.py`, which should have a single line that looks like this:

```
url = 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
```

Of course, insert the URL you got through the Slack API. The online interface allows you to specify what channel you would like it to post to, what the avatar should be for that bot, and some other features like that.

## Launching the backend

The backend can be launched in one fell swoop using the following command:

```
./1-stream-ingest.py
```

When you run this command, you should soon start to see small JSON strings popping up in stdout, which may look something like this:

```
{"delta": 0}
{"delta": 1}
{"delta": 0}
```

If so, you're in business! If not, make sure Redis server is running on the default port.

If you so choose, you can also run the backend manually using the following command:

```
python ingest.py | python diff.py | python redis-insert.py
```

## Launching the frontend

**Important:** You should wait a few minutes after starting the backend before you start the frontend, as discussed above. My recommendation would be to wait for at least 3 minutes. Nothing will go wrong, per se, if you launch it immediately, you may get some wonky values at first.

The frontend can be launched all at once using the following command:

```
./2-notifications.sh
```

If you would prefer, you can also launch it manually using the following command:

```
python avg.py | python find-anomalies.py | python slack.py
```

### Testing

Anomalies are, by definition, anomalous—they don't happen very often. As such, it may take a long time (possibly a very long time) for any messages to be output. My suggestion for verifying that the system is working would be the following.

- Start the backend and wait a few minutes.
- Instead of running `2-notifications.sh`, instead run `python ingest.py`. This will spit out the average rate to the command line. Based on this, you can find a threshold that is more likely to be triggered while you are watching at that particular moment.
- Open `find-anomalies.py` in the editor of your choosing and modify the THRESHOLD parameter (which is around line 56) to a number more likely to trigger a notification.
- Finally, you can run `2-notifications.sh`. It still may take a while, you could open a new terminal window and run `python ingest.py` again to check on the averages.