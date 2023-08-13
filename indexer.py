import nltk
import glob
import time
import math
import os
import requests
import sys
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# downloader = nltk.downloader.Downloader(download_dir='~/.nltk_data/')
# downloader.download('punkt')
# criar pastas visiveis no diretório home do usuario é feio
nltk.download('punkt')
ps = nltk.stem.PorterStemmer()

# toda a idea por trás desse programa:
# https://en.wikipedia.org/wiki/Tf%E2%80%93idf


class website():
    term_frequency = {}
    tf_idf = {}
    url = ""
    title = ""
    shouldIndex = False
    request = None

    def __init__(self, url, new):
        self.url = url
        self.tf_idf = {}
        self.term_frequency = {}

        self.new = new

    def download_page(self):
        print('download', self.url)
        self.request = requests.get(self.url)

    def is_html(self):
        return self.request.headers['content-type'].find('text/html') >= 0

    def __repr__(self):
        return self.url

    def calculate_term_freq(self):
        soup = BeautifulSoup(self.request.content, 'html.parser')

        self.title = soup.find('title').getText()

        tags = ['p', 'dd', 'dt', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        text = soup.findAll(tags)
        text = [i.getText().lower() for i in text]
        text = ' '.join(text)

        tokens = nltk.word_tokenize(text)
        tokens = [ps.stem(i) for i in tokens]

        count = {}
        for i in tokens:
            if i not in count:
                count[i] = 0
            count[i] += 1

        term_frequency = {}
        for k, v in count.items():
            term_frequency[k] = v / len(tokens)

        self.term_frequency = term_frequency

    def calculate_tf_idf(self, inverse_doc_frequency):
        for k, term_freq in self.term_frequency.items():
            self.tf_idf[k] = inverse_doc_frequency[k] * term_freq


def read_page(filename):
    with open(filename) as file:
        load = json.loads(file.read())
        page = website(load['url'], False)
        page.tf_idf = load['tf_idf']
        page.term_frequency = load['term_freq']
        page.title = load['title']
    return page


def save_to_index(page):
    print("index", page.url)
    formatted_name = '_'.join(page.url.split('/'))
    with open('index/' + formatted_name + '.json', "w") as file:
        file.write(json.dumps(
            {
                "url": page.url,
                "title": page.title,
                "time": time.time(),
                "tf_idf": page.tf_idf,
                "term_freq": page.term_frequency,
                }
            ))


# aka idf
def calculate_inverse_doc_frequency(reverse_index, documents_number):
    inverse_doc_frequency = {}
    for k, v in reverse_index.items():
        inverse_doc_frequency[k] = -math.log(len(v) / documents_number)
    return inverse_doc_frequency


def load_corpus():
    print('loading index...')
    corpus = []
    if os.path.exists('index'):
        for filename in glob.glob("index/*"):
            if os.path.isfile(filename):
                document = read_page(filename)
                corpus.append(document)
    return corpus


def add_to_reverse_index(reverse_index, page):
    # um indice reverso no nosso caso é um hashmap onde cada chave
    # contem uma palavra enquanto cada valor de cada chave é uma
    # lista com os documentos que possuem aquela palavra.
    # isso agiliza calcular o IDF.
    for k, v in page.term_frequency.items():
        if k not in reverse_index:
            reverse_index[k] = []
        reverse_index[k].append(page.url)


def read_new_urls():
    urls = []
    if not os.path.exists('urls.txt'):
        print('urls.txt?', file=sys.stderr)
        sys.exit(1)

    with open('urls.txt') as file:
        urls = [line.rstrip('\n') for line in file]
        urls = [urlparse(url)._replace(
            query='', fragment='', params='').geturl() for url in urls]
        urls = list(set(urls))

    empty_urls_file = not urls
    if empty_urls_file:
        print('urls.txt?', file=sys.stderr)
        sys.exit(1)
    return urls


def remove_duplicates(urls, indexed_corpus):
    indexed_urls = [i.url for i in indexed_corpus]
    s = set(indexed_urls)
    return [i for i in urls if i not in s]


def recalculate(indexed_corpus, reverse_index):
    # todo: assíncrono
    documents_number = len(indexed_corpus)

    for index, page in enumerate(indexed_corpus):
        print(f'({documents_number-index} left to go) \
recalculating, {page.url}')
        inverse_doc_frequency = calculate_inverse_doc_frequency(
                reverse_index, documents_number
                )
        page.calculate_tf_idf(inverse_doc_frequency)
        save_to_index(page)


def main():
    urls = []
    isRecalculate = False
    update = False
    indexed_corpus = []
    # last_time = 0
    documents_number = 0
    reverse_index = {}

    if not os.path.exists('index'):
        os.makedirs('index')

    if len(sys.argv) > 1 and sys.argv[1] == 'recalculate':
        isRecalculate = True
    elif len(sys.argv) > 1 and sys.argv[1] == 'update':
        update = True

    read_from_url_list = not isRecalculate and not update

    if read_from_url_list:
        urls = read_new_urls()

    # print('load corpus')
    indexed_corpus = load_corpus()

    [add_to_reverse_index(reverse_index, i) for i in indexed_corpus]

    urls = remove_duplicates(urls, indexed_corpus)

    if update:
        urls += [page.url for page in indexed_corpus]
        indexed_corpus = []
    elif isRecalculate:
        print('skipping new urls and performing recalculation...')
        recalculate(indexed_corpus, reverse_index)
        sys.exit(0)

    print('urls', len(urls))
    for url in urls:
        page = website(url, True)

        page.download_page()
        if not page.is_html():
            continue

        page.calculate_term_freq()
        add_to_reverse_index(reverse_index, page)
        documents_number = len(urls) + len(indexed_corpus)

        inverse_doc_frequency = calculate_inverse_doc_frequency(
                reverse_index, documents_number
                )
        page.calculate_tf_idf(inverse_doc_frequency)
        save_to_index(page)

    with open('urls.txt', 'w') as file:
        file.write('')


if __name__ == "__main__":
    main()
