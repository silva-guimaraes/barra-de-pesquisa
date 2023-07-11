import requests
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


if len(sys.argv) == 1:
    print('len(sys.argv) == 1')
    sys.exit(1)


def get_anchors(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    anchors = soup.find_all('a')
    return [i.get('href') for i in anchors]


def same_domain(base_domain, url):
    return True if url.find(base_domain) != -1 else False


def complete_link(base_domain, url):
    return urljoin(base_domain, url)


def trim_url(url):
    return urlparse(url)._replace(fragment='', query='', params='').geturl()


def remove_duplicates(links):
    return list(set(links))


# Example usage
website_url = sys.argv[1]
domain = urlparse(website_url).netloc
anchors = get_anchors(website_url)

links = [complete_link(website_url, link) for link in anchors]

links = [trim_url(link) for link in links if same_domain(domain, link)]

links = remove_duplicates(links)

[print(link) for link in links]
