# find-unlikely.py
# Jonah Smith

from sys import stdin, stdout
import json
import util

while 1:
    line = stdin.readline()
    edit = json.loads(line)

    title = edit.get('title')

    prob = util.probability(title)

    # Because the Wikipedia corpus is so big, we are basically only surprised
    # when we see an edit to a page we have never seen an edit to before, e.g.
    # estimated probability 0.
    if prob == 0:
        alert = {
                  'type': 'unlikely_message',
                  'title': title,
                  'prob': prob
                }
        print(json.dumps(alert))
        stdout.flush()
