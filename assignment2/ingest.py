# ingest.py
# Jonah Smith
# Storytelling with Streaming Data, Spring 2016
#
# This script ingests a socket.io websocket produced by Wikimedia. The socket
# spits out changes to Wikipedia changes as they are made. The schema is
# available here: https://www.mediawiki.org/wiki/Manual:RCFeed#Properties
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

# This class is used to process messages over the RC Socket.IO channel.
class WikiNamespace(BaseNamespace):

    # Run when this client receives a message.
    def on_change(self, change):
        # The 0 namespace is for 'real content' like articles (as opposed to
        # media, category pages, etc), so we will filter for it. Via:
        # https://www.mediawiki.org/wiki/Manual:Namespace#Built-in_namespaces
        if change.get('namespace') == 0:
            # Print the edits to 'real content' verbatim as a JSON to stdout,
            # to be processed by diff.py.
            print(json.dumps(change))
            # As always, flush stdout to get it to print without getting put in
            # a buffer!
            stdout.flush()

    # When the client connects, we need to subscribe to the English Wikipedia
    # stream. I figured out the correct argument for 'subscribe' through an
    # educated guess.
    def on_connect(self):
        self.emit('subscribe', 'en.wikipedia.org')

# Establish the connection with the SocketIO client.
socket = SocketIO('stream.wikimedia.org', 80)

# Set the '/rc' channel (which has realtime changes) to the handler class
# defined above.
socket.define(WikiNamespace, '/rc')

# Now set up the socket and start waiting.
socket.wait()
