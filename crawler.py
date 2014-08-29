#!/usr/bin/env python
import re
import logging
import requests
from pprint import pprint

from BeautifulSoup import BeautifulStoneSoup as Soup


logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    level=logging.WARNING
)

ROOT_URL = 'http://epocacosmeticos.com.br/sitemap.xml'
PRODUCTS_REGEX = re.compile(r'sitemap-produtos.*\.xml')
PRODUCT_NAME_REGEX = re.compile(r'\bproductName\b')


def make_request(url, allow_redirects=False):
    logging.info('making a request to [%s]' % url)
    response = requests.get(url, allow_redirects=allow_redirects)
    if (not allow_redirects) and (response.status_code in (301, 302)):
        data = None
    else:
        data = response.content
    logging.debug('data: %s' % data)
    return data


def extract_product_sitemaps(response):
    logging.info('extracting product sitemaps...')
    soup = Soup(response)
    return soup.findAll('loc', text=PRODUCTS_REGEX)


def extract_product_urls(url):
    logging.info('extracting product urls from [%s]...' % url)
    response = make_request(url)
    soup = Soup(response)
    loc = soup.findAll('loc')
    for url in loc:
        yield url.text


def grab_product_details(url):
    logging.info('grabbing product details [%s]' % url)
    response = make_request(url, False)
    data = None
    if response is not None:
        logging.info('found product url [%s]' % url)
        soup = Soup(response)
        page_title = soup.title.string
        product_name = soup(attrs={'class': PRODUCT_NAME_REGEX})[0].string
        data = {
            'page_url': url,
            'page_title': page_title,
            'product_name': product_name
        }
    else:
        logging.warning('skipping product url [%s]' % url)
    return data


def main():
    logging.info('crawler has been started')
    response = make_request(ROOT_URL, True)
    product_sitemaps = extract_product_sitemaps(response)

    for sitemap_url in product_sitemaps:
        for product_url in extract_product_urls(sitemap_url):
            data = grab_product_details(product_url)
            pprint(data)

    logging.info('crawler finished')


if __name__ == '__main__':
    main()
