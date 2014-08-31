#!/usr/bin/env python
# -*- coding: utf-8 -*-

# stdlib
import os
import sys
import logging
import re
import codecs
import urlparse
import robotexclusionrulesparser

# gevent
import gevent
import gevent.queue

# gevent monkey patching
from gevent import monkey
monkey.patch_all()

# requests
import requests

# beautifulsoup
from BeautifulSoup import BeautifulStoneSoup as Soup

# take the script filename without the extension so we can properly name files
# produced by this solution
SOLUTION_NAME = os.path.splitext(os.path.basename(__file__))[0]

# define the allowed domain to follow links
ALLOWED_DOMAIN = 'epocacosmeticos.com.br'

# define a blacklist
BLACKLIST_REGEX = re.compile(
    r'('
    r'\?PS\=20\&map'
    r'|checkout\/cart\/add'
    r'|^mailto\:'
    r')'
)

# the base url applied to relative links
BASE_URL = 'http://%s' % ALLOWED_DOMAIN

# the starting point url
INITIAL_URL = BASE_URL

# used to find the product name within the product details page
# by the way, productName is one css classes of the tag that
# encapsulates the actual name of the product
PRODUCT_NAME_REGEX = re.compile(r'\bproductName\b')

# the product page url format
PRODUCT_PAGE_REGEX = re.compile(r'.*\/p$')

# define the output csv filename
CSV_FILENAME = 'data/%s.csv' % SOLUTION_NAME

# some formatting settings for the csv file to be generated
# it's possible to change the headers (column name) and the order of the fields
CSV_HEADERS = u'product_name,page_title,page_url\n'
CSV_FORMAT = u'"%(product_name)s","%(page_title)s","%(page_url)s"\n'


# define the maximum number of workers (greenlets)
MAX_WORKERS = 10


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

# ---------------------------------------

logger.info('crawler has been started')

# prevent some encoding problems
reload(sys)
sys.setdefaultencoding("utf-8")

# load robot rules
RERP = robotexclusionrulesparser.RobotExclusionRulesParser()
RERP.fetch(urlparse.urljoin(BASE_URL, '/robots.txt'))

# open the output file
csv = codecs.open(CSV_FILENAME, 'w', 'utf-8')
csv.write(CSV_HEADERS)

# ---------------------------------------

queue = gevent.queue.JoinableQueue()
discovered = set()
visited = []

# ---------------------------------------


def can_visit_link(url):
    return (url not in discovered) \
        and (ALLOWED_DOMAIN in url) \
        and RERP.is_allowed('*', url) \
        and not BLACKLIST_REGEX.search(url)


def discover_links(url, soup):
    logger.info('discovering links for [%s]' % url)
    anchors = soup.findAll('a', href=True)
    for anchor in anchors:
        href = anchor['href']
        if href and href.strip().startswith('#'):
            logger.debug('ignoring [%s]' % href)
            continue
        new_url = urlparse.urljoin(BASE_URL, href).strip()
        logger.debug('new url found: [%s]' % new_url)
        if can_visit_link(new_url):
            logger.info('adding new url to the queue [%s]' % new_url)
            discovered.add(new_url)
            queue.put(new_url)


def extract_product_data(url, soup):
    """ extract required data from the product details page
    """
    logger.info('grabbing product details from [%s]' % url)
    page_title = soup.title.string
    product_name = soup(attrs={'class': PRODUCT_NAME_REGEX})[0].string
    data = {
        'page_url': url,
        'page_title': page_title,
        'product_name': product_name
    }
    return data


def is_valid_product_page(url, response):
    return PRODUCT_PAGE_REGEX.match(url) and \
        'ProductLinkNotFound' not in response.url


def crawler(n):
    while True:
        logger.info(
            'links: [%d] pending, [%d] discovered, [%d] visited'
            % (queue.qsize(), len(discovered), len(visited))
        )
        url = queue.get()
        logger.info('crawler [%d] took [%s] from queue' % (n, url))
        response = requests.get(url, verify=False)  # no SSL validation
        visited.append(url)
        if response.status_code == requests.codes.ok:
            soup = Soup(response.content)
            if is_valid_product_page(url, response):
                data = extract_product_data(url, soup)
                csv.write(CSV_FORMAT % data)
            discover_links(url, soup)
        else:
            logger.warning('response not ok for [%s]' % url)
        queue.task_done()


for n in xrange(MAX_WORKERS):
    gevent.spawn(crawler, n)


queue.put(INITIAL_URL)
discovered.add(INITIAL_URL)
visited.append(INITIAL_URL)

queue.join()

# close the output file
csv.close()

logger.info('crawler finished')