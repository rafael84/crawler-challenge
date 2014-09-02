#!/usr/bin/env python

# stdlib
import re
import logging
import unittest

# gevent
import gevent
import gevent.queue

# beautifulsoup
from BeautifulSoup import BeautifulStoneSoup as Soup

# robot exclusion rules parser
from robotexclusionrulesparser import RobotExclusionRulesParser

# mock
import mock

# solution one
import solution_one


logging.basicConfig()
logger = logging.getLogger()


class SolutionOneTestCase(unittest.TestCase):

    def setUp(self):
        solution_one.ALLOWED_DOMAIN = 'test.com'
        solution_one.BASE_URL = 'http://test.com'
        solution_one.BLACKLIST_REGEX = re.compile(r'^mailto\:')
        solution_one.RERP = RobotExclusionRulesParser()
        solution_one.RERP.parse('User-Agent: *')

        solution_one.logger = logger
        solution_one.queue = gevent.queue.JoinableQueue()
        solution_one.visited = []
        solution_one.discovered = set()


class TestDiscoverLinks(SolutionOneTestCase):

    def test_should_ignore_links_starting_with_hashtag(self):
        html = '''<a href="#top">Top</a>'''
        soup = Soup(markup=html)
        solution_one.discover_links(url='', soup=soup)
        self.assertEquals(0, solution_one.queue.qsize())

    def test_should_add_allowed_urls_to_queue(self):
        html = '''
            <a href="/valid">Valid</a>
            <a href="#invalid">Invalid</a>
            <a href="mailto://invalid@invalid.com">Invalid Too</a>
            <a href="/also-valid">Also Valid</a>
        '''
        soup = Soup(markup=html)
        solution_one.discover_links(url='', soup=soup)
        self.assertEquals(2, solution_one.queue.qsize())


class TestCanVisitLink(SolutionOneTestCase):

    def test_should_check_the_black_list(self):
        pattern = r'/private'
        solution_one.BLACKLIST_REGEX = re.compile(pattern)
        solution_one.BASE_URL = 'http://test.com'
        html = '''
            <a href="http://test.com/private">Private</a>
            <a href="http://test.com/public">Public</a>
        '''
        soup = Soup(markup=html)
        solution_one.discover_links(url='', soup=soup)
        self.assertEquals(1, solution_one.queue.qsize())


if __name__ == '__main__':
    unittest.main()
