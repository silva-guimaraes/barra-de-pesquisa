import os
import glob
import nltk
import json
import flask

app = flask.Flask(__name__, template_folder='pages')


class website():
    term_frequency = {}
    tf_idf = {}
    url = ""
    shouldIndex = False

    def __init__(self, url, shouldIndex):
        self.url = url
        self.tf_idf = {}
        self.term_frequency = {}

        self.shouldIndex = shouldIndex

    def __repr__(self):
        return self.url


class candidateWebsite():

    def __init__(self, website):
        self.website = website
        self.score = 0
        self.matched_words = {}

    def __repr__(self):
        return f'<url: {self.website.url} | score: {self.score}>'


def read_page(filename):
    with open(filename) as file:
        load = json.loads(file.read())
        page = website(load['url'], False)
        page.tf_idf = load['tf_idf']
        page.term_frequency = load['term_freq']
    return page


def load_websites():
    websites = []
    if os.path.exists('index'):
        for filename in glob.glob("index/*"):
            if os.path.isfile(filename):
                websites.append(read_page(filename))
    return websites


@app.route('/')
def hello():
    search = flask.request.args.get('search')
    print(search)

    if search is None:
        return flask.send_file('pages/index.html')

    tokens = nltk.word_tokenize(search)

    websites = load_websites()
    candidates = [candidateWebsite(website) for website in websites]

    for candidate in candidates:
        for word in tokens:
            try:
                score = candidate.website.tf_idf[word]
                candidate.score += score
                candidate.matched_words[word] = score
            except KeyError:
                continue

    candidates = sorted(candidates, reverse=True, key=lambda i: i.score)
    candidates = [i for i in candidates if i.score > 0]

    print(candidates)

    return flask.render_template(
            'search.html',
            terms=search,
            candidates=candidates,
            )


@app.route('/<path:path>')
def serve_file(path):
    return flask.send_from_directory('pages', path)
