#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import re
import logging
import codecs

import requests
from BeautifulSoup import BeautifulStoneSoup as Soup

SOLUTION_NAME = os.path.splittext(os.path.basename(__file__))[0]

SITEMAP_URL = 'http://epocacosmeticos.com.br/sitemap.xml'
PRODUCTS_REGEX = re.compile(r'sitemap-produtos.*\.xml')
PRODUCT_NAME_REGEX = re.compile(r'\bproductName\b')

CSV_FILENAME = 'data/%s.csv' % SOLUTION_NAME
CSV_HEADERS = u'product_name,page_title,page_url\n'
CSV_FORMAT = u'"%(product_name)s","%(page_title)s","%(page_url)s"\n'

logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    level=logging.INFO,
    filename='logs/%s.log' % SOLUTION_NAME
)
logger = logging.getLogger(SOLUTION_NAME)


def make_request(url, allow_redirects=False):
    logger.info('making a request to [%s]' % url)
    response = requests.get(url, allow_redirects=allow_redirects)
    if (not allow_redirects) and (response.status_code in (301, 302)):
        data = None
    else:
        data = response.content
    logger.debug('data: %s' % data)
    return data


def extract_product_sitemaps():
    logger.info('extracting product sitemaps...')
    response = make_request(SITEMAP_URL, True)
    soup = Soup(response)
    return soup.findAll('loc', text=PRODUCTS_REGEX)


def extract_product_urls(url):
    logger.info('extracting product urls from [%s]...' % url)
    response = make_request(url)
    soup = Soup(response)
    loc = soup.findAll('loc')
    for url in loc:
        yield url.text


def extract_product_details(url):
    logger.info('grabbing product details [%s]' % url)
    response = make_request(url, False)
    data = None
    if response is not None:
        logger.info('found product url [%s]' % url)
        soup = Soup(response)
        page_title = soup.title.string
        product_name = soup(attrs={'class': PRODUCT_NAME_REGEX})[0].string
        data = {
            'page_url': url,
            'page_title': page_title,
            'product_name': product_name
        }
    else:
        logger.warning('skipping product url [%s]' % url)
    return data


def write_product_details(product_url, csv):
    try:
        data = extract_product_details(product_url)
        if data:
            csv.write(CSV_FORMAT % data)
    except Exception as ex:
        logger.error(
            'could not parse [%s], exception: [%s]'
            % (product_url, ex.message)
        )


def run():
    logger.info('crawler has been started')

    with codecs.open(CSV_FILENAME, 'w', 'utf-8') as csv:
        csv.write(CSV_HEADERS)
        product_sitemaps = extract_product_sitemaps()
        for sitemap_url in product_sitemaps:
            for product_url in extract_product_urls(sitemap_url):
                write_product_details(product_url, csv)

    logger.info('crawler finished')


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding("utf-8")
    run()
