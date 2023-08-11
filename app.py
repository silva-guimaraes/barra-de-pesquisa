import os
import glob
import random
import nltk
import json
from urllib.parse import urlparse
import flask

app = flask.Flask(__name__, template_folder='pages')


nltk.download('punkt')
ps = nltk.stem.PorterStemmer()


class website():
    term_frequency = {}
    tf_idf = {}
    url = ""
    title = ""
    shouldIndex = False

    def __init__(self, url, tf_idf, title):
        self.tf_idf = {}

        self.url = url
        self.tf_idf = tf_idf
        self.title = title

    def __repr__(self):
        return self.url


class candidateWebsite():
    def __init__(self, website):
        self.website = website
        self.score = 0
        self.matched_words = {}

    def __repr__(self):
        return f'<url: {self.website.url} | score: {self.score} | \
matched words: {self.matched_words}>'


def read_page(filename):
    with open(filename) as file:
        load = json.loads(file.read())
        return website(load['url'], load['tf_idf'], load['title'])


def load_websites():
    websites = []
    if os.path.exists('index'):
        for filename in glob.glob("index/*"):
            if os.path.isfile(filename):
                websites.append(read_page(filename))
    return websites


websites = load_websites()


# /index.html não funciona
@app.route('/')
def hello():
    search = flask.request.args.get('search')
    print(search)

    if search is None:
        print('index page')
        return flask.send_file('pages/index.html')

    tokens = nltk.word_tokenize(search)
    tokens = [ps.stem(i) for i in tokens]

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
    candidates = sorted(candidates, reverse=True,
                        key=lambda i: len(i.matched_words))

    candidates = [i for i in candidates if i.score > 0]

    candidates = candidates[:40]

    # debug
    for i in candidates:
        i.website.title = i.website.title + ' ' + json.dumps(i.matched_words)

    return flask.render_template(
            'search.html',
            terms=search,
            candidates=candidates,
            )


@app.route('/<path:path>')
def serve_file(path):
    return flask.send_from_directory('pages', path)


@app.route('/random')
def random_page():
    urls = [page.url for page in websites]
    urls = [urlparse(url)._replace(scheme='', path='').geturl()
            for url in urls]
    urls = list(set(urls))
    random.shuffle(urls)
    return flask.redirect(urls[0])


@app.errorhandler(404)
def error():
    return '404'
