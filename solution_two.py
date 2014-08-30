#!/usr/bin/env python
# -*- coding: utf-8 -*-

# stdlib
import os
import sys
import re
import logging
import codecs

# requests
import requests

# beautifulsoup
from BeautifulSoup import BeautifulStoneSoup as Soup

# take the script filename without the extension so we can properly name files
# produced by this solution
SOLUTION_NAME = os.path.splitext(os.path.basename(__file__))[0]

# the url of sitemap used as the starting point for this solution
SITEMAP_URL = 'http://epocacosmeticos.com.br/sitemap.xml'

# the root sitemap points to other specific sitemaps
# we are interested only on the ones that are related to products
PRODUCTS_REGEX = re.compile(r'sitemap-produtos.*\.xml')

# used to find the product name within the product details page
# by the way, productName is one css classes of the tag that
# encapsulates the actual name of the product
PRODUCT_NAME_REGEX = re.compile(r'\bproductName\b')

# define the output csv filename
CSV_FILENAME = 'data/%s.csv' % SOLUTION_NAME

# some formatting settings for the csv file to be generated
# it's possible to change the headers (column name) and the order of the fields
CSV_HEADERS = u'product_name,page_title,page_url\n'
CSV_FORMAT = u'"%(product_name)s","%(page_title)s","%(page_url)s"\n'


# make sure the required directories exists
if not os.path.exists('data'):
    os.makedirs('data')
if not os.path.exists('logs'):
    os.makedirs('logs')


# configure the logging
logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    level=logging.INFO,
    filename='logs/%s.log' % SOLUTION_NAME
)
logger = logging.getLogger(SOLUTION_NAME)


def curl(url, allow_redirects=False):
    """ make a request to the url, returning the response content

    when allow_redirects is False and the http response has a redirect
    status code (301, 302) then None is returned, otherwise the original
    response content is returned.
    """
    logger.info('making a request to [%s]' % url)
    response = requests.get(url, allow_redirects=allow_redirects)
    if (not allow_redirects) and (response.status_code in (301, 302)):
        data = None
    else:
        data = response.content
    logger.debug('data: %s' % data)
    return data


def extract_product_sitemaps():
    """ return a list of product sitemaps from the root sitemap
    """
    logger.info('extracting product sitemaps...')
    response = curl(SITEMAP_URL, True)
    soup = Soup(response)
    return soup.findAll('loc', text=PRODUCTS_REGEX)


def extract_product_urls(url):
    """ get all product urls from a product sitemap
    """
    logger.info('extracting product urls from [%s]...' % url)
    response = curl(url)
    soup = Soup(response)
    loc = soup.findAll('loc')
    for url in loc:
        yield url.text


def extract_product_data(url):
    """ extract required data from the product details page
    """
    logger.info('grabbing product details [%s]' % url)
    response = curl(url)  # no redirects allowed!
    data = None
    if response is not None:
        # product page has been found, we can extract its details
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
        # product page has not been found, probably because the
        # sitemap is outdated :(
        logger.warning('skipping product url [%s]' % url)
    return data


def write_product_data(product_url, csv):
    """ take product details from the product page and append it to the csv file
    """
    try:
        data = extract_product_data(product_url)
        if data:
            csv.write(CSV_FORMAT % data)
    except Exception as ex:
        logger.error(
            'could not write product data from [%s], exception: [%s]'
            % (product_url, ex.message)
        )


def run():
    """ the solution entry point

    the logic here is pretty straightforward:
    1. open the output filename
    2. get the root sitemap
    3. get the product sitemaps from the root sitemap
    4. access each product url and take the required data from it

    depending on your network bandwidth, the whole process may take up to
    two hours to complete.
    """
    logger.info('crawler has been started')

    # prevent some encoding problems
    reload(sys)
    sys.setdefaultencoding("utf-8")

    with codecs.open(CSV_FILENAME, 'w', 'utf-8') as csv:
        csv.write(CSV_HEADERS)
        product_sitemaps = extract_product_sitemaps()
        for sitemap_url in product_sitemaps:
            for product_url in extract_product_urls(sitemap_url):
                write_product_data(product_url, csv)

    logger.info('crawler finished')


if __name__ == '__main__':
    run()
