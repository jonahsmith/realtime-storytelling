# ingest.py
# Jonah Smith
# Assignment 3, Storytelling with Streaming Data, Spring 2016
#
# (Some of this code originally appeared in my submission for Assignment 2)
#
# This script ingests a socket.io websocket produced by Wikimedia. The socket
# spits out changes to Wikipedia changes as they are made. The schema is
# available here: https://www.mediawiki.org/wiki/Manual:RCFeed#Properties
# This version subscribes to the top twelve largest Wikipedias.
#
# Note: this ingestion code is based on the example provided by Wikipedia:
# https://wikitech.wikimedia.org/wiki/RCStream#Python

from sys import stdout
import logging
import json
from socketIO_client import SocketIO, BaseNamespace

# By default, the socketIO_client library logs things. Unfortunately, that will
# mess with outputting things via stdout. As such, we're going to escalate the
# logging level to CRITICAL--e.g. it'll only output things if something really
# bad happens. That will break the pipe, probably, but that's probably for the
# best, as it will require our attention anyway.
logging.basicConfig(level=logging.CRITICAL)


# These are the thirteen biggest Wikipedias by article size, as measured by:
# https://en.wikipedia.org/wiki/List_of_Wikipedias I have selected these because
# they are the only Wikis with over one million articles, which I think captures
# the idea of a 'big' Wikipedia language site.
languages = ('en.wikipedia.org', 'sv.wikipedia.org', 'ceb.wikipedia.org',
             'de.wikipedia.org', 'nl.wikipedia.org', 'fr.wikipedia.org',
             'ru.wikipedia.org', 'war.wikipedia.org', 'it.wikipedia.org',
             'es.wikipedia.org', 'pl.wikipedia.org', 'vi.wikipedia.org',
             'ja.wikipedia.org')


# This class is used to process messages over the RC Socket.IO channel.
class WikiNamespace(BaseNamespace):

    # Run when this client receives a message.
    def on_change(self, change):
        # The 0 namespace is for 'real content' like articles (as opposed to
        # media, category pages, etc), so we will filter for it.
        if change.get('namespace') == 0:
            # Print the edits to 'real content' verbatim as a JSON to stdout,
            # to be processed by diff.py.
            print(json.dumps(change))
            # As always, flush stdout to get it to print without getting put in
            # a buffer!
            stdout.flush()

    # When the client connects, we need to subscribe to the Wikipedias for the
    # languages declared above.
    def on_connect(self):
        for lang in languages:
            self.emit('subscribe', lang)

# Establish the connection with the SocketIO client.
socket = SocketIO('stream.wikimedia.org', 80)

# Set the '/rc' channel (which has realtime changes) to the handler class
# defined above.
socket.define(WikiNamespace, '/rc')

# Now set up the socket and start waiting.
socket.wait()
