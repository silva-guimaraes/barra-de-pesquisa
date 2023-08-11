import requests
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def get_href(url):
    response = requests.get(url)
    if response.status_code != 200:
        print('response.status_code != 200', file=sys.stderr)
        sys.exit(1)
    soup = BeautifulSoup(response.content, 'html.parser')
    anchors = soup.select('a')
    return [i.get('href') for i in anchors]


def same_domain(base_domain, url):
    return True if url.find(base_domain) != -1 else False


def complete_link(base_domain, url):
    return urljoin(base_domain, url)


def trim_url(url):
    return urlparse(url)._replace(fragment='', query='', params='').geturl()


def remove_duplicates(links):
    return list(set(links))


def has_double_dot_segments(url):
    return True if url.find('..') != -1 else False


def extract_links(website_url, same_domain_only):
    domain = urlparse(website_url).netloc

    links = get_href(website_url)

    links = [link for link in links if link is not None]

    links = [link for link in links if not has_double_dot_segments(link)]

    links = [complete_link(website_url, link) for link in links]

    if same_domain_only:
        links = [trim_url(link) for link in links if same_domain(domain, link)]
    else:
        links = [trim_url(link) for link in links
                 if not same_domain(domain, link)]

    return remove_duplicates(links)


def main():
    if len(sys.argv) == 1:
        print('len(sys.argv) == 1')
        sys.exit(1)

    website_url = sys.argv[1]
    same_domain_only = True

    if len(sys.argv) > 2 and sys.argv[2] == 'external':
        same_domain_only = False

    [print(link) for link in extract_links(website_url, same_domain_only)]


if __name__ == "__main__":
    print('foo')
    main()
