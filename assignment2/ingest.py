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

logging.basicConfig(level=logging.CRITICAL)


# This class is used to process messages over the RC Socket.IO channel.
class WikiNamespace(BaseNamespace):

    # Run when this client receives a message.
    def on_change(self, change):
        # The 0 namespace is for 'real content' like articles (as opposed to
        # media, category pages, etc), so we will filter for it.
        # https://www.mediawiki.org/wiki/Manual:Namespace#Built-in_namespaces
        if change.get('namespace') == 0:
            print(json.dumps(change))
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

socket.wait()
