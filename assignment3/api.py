# api.py
# Jonah Smith
# Assignment 3, Storytelling with Streaming Data, Spring 2016
#
# This script connects to a Redis database (table 0 with time diffs between
# events, table 1 with a distribution over articles), and defines an API to
# access certain calculations, including the rate, the histogram, the entropy,
# and the probability of a given message.

from flask import Flask, request, render_template
import json
import util

app = Flask(__name__)


@app.route('/rate')
def get_rate():
    rate = util.rate()
    return json.dumps( {'avg_rate': rate})


@app.route('/histogram')
def get_histogram():
    hist = util.histogram()
    return json.dumps(hist)


@app.route('/entropy')
def get_entropy():
    entropy = util.entropy()
    return json.dumps({'entropy': entropy})


@app.route('/probability')
def get_probability():
    msg = request.args.get('message')
    if not title:
        return json.dumps({'error': 'no \'message\' argument given'})
    prob = util.probability(msg)
    response = { 'message': msg, 'p': prob }
    return json.dumps(response)


@app.route('/vis')
def get_vis():
    return render_template('histogram.html')


if __name__ == '__main__':
    app.run(debug=True)
