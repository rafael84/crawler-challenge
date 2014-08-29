#!/usr/bin/env python
import re
import logging
import urllib2

from StringIO import StringIO
import gzip

from BeautifulSoup import BeautifulStoneSoup as Soup

logging.basicConfig(level=logging.INFO)

ROOT_URL = 'http://epocacosmeticos.com.br/sitemap.xml'
PRODUCTS_REGEX = r'sitemap-produtos.*\.xml'


def make_request(url):
    logging.info('making a request to [%s]' % url)
    request = urllib2.Request(url)
    request.add_header('Accept-encoding', 'gzip')
    response = urllib2.urlopen(request)
    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
    else:
        data = response.read()
    logging.debug('data: %s' % data)
    return data


def extract_product_sitemaps(response):
    logging.info('extracting product sitemaps...')
    soup = Soup(response)
    return soup.findAll('loc', text=re.compile(PRODUCTS_REGEX))


def extract_product_urls(url):
    logging.info('extracting product urls from [%s]...' % url)
    response = make_request(url)
    soup = Soup(response)
    loc = soup.findAll('loc')
    for url in loc:
        yield url.text


if __name__ == '__main__':
    logging.info('crawler has been started')
    product_sitemaps = extract_product_sitemaps(make_request(ROOT_URL))

    products = []
    for url in product_sitemaps:
        products.extend(list(extract_product_urls(url)))

    from pprint import pprint
    pprint(products)

    logging.info('COUNT: %d' % len(products))

    logging.info('crawler finished')
