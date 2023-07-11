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

nltk.download('punkt')
# ps = nltk.stem.PorterStemmer()

# atribui valores altos para termos que tenham relevacia para uma pagina
# porem ao mesmo tempo nao aparecendo com frequencia em outras paginas.
# termos relevantes sao termos que aparecem com frequencia em uma pagina.
# termos que aparecem com frequencia em todas as paginas
# recebem valores baixos.
# https://en.wikipedia.org/wiki/Tf%E2%80%93idf
# é perfeito pra distinguir uma pagina da outra


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

    def calculate_term_freq(self):
        ret = requests.get(self.url)

        soup = BeautifulSoup(ret.content, 'html.parser')

        tags = ['p', 'dd', 'dt', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        text = soup.findAll(tags)
        text = [i.getText().lower() for i in text]
        text = ' '.join(text)

        tokens = nltk.word_tokenize(text)
        # tokens = [ps.stem(i) for i in tokens]

        count = {}
        for i in tokens:
            if i not in count:
                count[i] = 0
            count[i] += 1

        term_frequency = {}
        for k, v in count.items():
            term_frequency[k] = v / len(tokens)

        self.term_frequency = term_frequency


def read_page(filename):
    with open(filename) as file:
        load = json.loads(file.read())
        page = website(load['url'], False)
        page.tf_idf = load['tf_idf']
        page.term_frequency = load['term_freq']
    return page


urls = []
refresh = False
reverse_index = {}
websites = []
last_time = 0
documents_number = 0
reverse_index = {}

if len(sys.argv) > 1 and sys.argv[1] == 'refresh':
    refresh = True

read_from_url_list = not refresh

if read_from_url_list:
    if os.path.exists('urls.txt'):
        with open('urls.txt') as file:
            urls = [line.rstrip('\n') for line in file]
            urls = [urlparse(url)._replace(
                query='', fragment='', params='').geturl() for url in urls]
            urls = list(set(urls))

        empty_urls_file = not urls

        if empty_urls_file:
            print('urls.txt?', file=sys.stderr)
            sys.exit(1)
    else:
        print('urls.txt?', file=sys.stderr)
        sys.exit(1)

# carregar todos os sites indexados e calcular o indice reverso
if os.path.exists('index'):
    for filename in glob.glob("index/*"):
        if os.path.isfile(filename):
            websites.append(read_page(filename))
for page in websites:
    for k, v in page.term_frequency.items():
        if k not in reverse_index:
            reverse_index[k] = []
        reverse_index[k].append(page.url)

documents_number = len(urls) + len(websites)

for url in urls:
    print("download", url)
    page = website(url, True)
    page.calculate_term_freq()
    websites.append(page)
    for k, v in page.term_frequency.items():
        if k not in reverse_index:
            reverse_index[k] = []
        reverse_index[k].append(url)

inverse_doc_frequency = {}
for k, v in reverse_index.items():
    inverse_doc_frequency[k] = -(math.log(len(v) / documents_number))


only_new_url = not refresh

if only_new_url:
    websites = [page for page in websites if page.shouldIndex]

for page in websites:
    for k, term_freq in page.term_frequency.items():
        page.tf_idf[k] = inverse_doc_frequency[k] * term_freq

if not os.path.exists('index'):
    os.makedirs('index')

for page in websites:
    print("index", page.url)
    formatted_name = '_'.join(page.url.split('/'))
    with open('index/' + formatted_name + '.json', "w") as file:
        file.write(json.dumps(
            {
                "url": page.url,
                "time": time.time(),
                "tf_idf": page.tf_idf,
                "term_freq": page.term_frequency,
                }
            ))

with open('urls.txt', 'w') as file:
    file.write('')
