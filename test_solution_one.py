#!/usr/bin/env python

# stdlib
import sys
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

    def test_should_ignore_links_without_href(self):
        html = '''<a class='href'>no href</a>'''
        soup = Soup(markup=html)
        solution_one.discover_links(url='', soup=soup)
        self.assertEquals(0, solution_one.queue.qsize())
        self.assertEquals(0, len(solution_one.discovered))

    def test_should_ignore_links_starting_with_hashtag(self):
        html = '''<a href="#top">Top</a>'''
        soup = Soup(markup=html)
        solution_one.discover_links(url='', soup=soup)
        self.assertEquals(0, solution_one.queue.qsize())
        self.assertEquals(0, len(solution_one.discovered))

    def test_should_add_allowed_urls_to_queue_and_discovered(self):
        html = '''
            <a href="/valid">Valid</a>
            <a href="#invalid">Invalid</a>
            <a href="mailto://invalid@invalid.com">Invalid Too</a>
            <a href="/also-valid">Also Valid</a>
        '''
        soup = Soup(markup=html)
        solution_one.discover_links(url='', soup=soup)
        self.assertEquals(2, solution_one.queue.qsize())
        self.assertEquals(2, len(solution_one.discovered))

    def test_should_treat_relative_links_properly(self):
        html = '''
            <a href="/relative">Relative</a>
            <a href="http://test.com/absolule">Absolute</a>
        '''
        soup = Soup(markup=html)
        solution_one.discover_links(url='', soup=soup)
        self.assertEquals(2, solution_one.queue.qsize())
        self.assertEquals(2, len(solution_one.discovered))


class TestCanVisitLink(SolutionOneTestCase):

    def test_should_check_the_black_list(self):
        solution_one.BLACKLIST_REGEX = re.compile(r'/private')
        url = 'http://test.com/private'
        self.assertFalse(solution_one.can_visit_link(url))
        url = 'http://test.com/public'
        self.assertTrue(solution_one.can_visit_link(url))

    def test_should_not_allow_the_same_url_twice(self):
        url = 'http://test.com/twice'
        self.assertTrue(solution_one.can_visit_link(url))
        solution_one.discovered = [url, ]
        self.assertFalse(solution_one.can_visit_link(url))

    def test_should_not_allow_external_links(self):
        url = 'http://test.com/internal'
        self.assertTrue(solution_one.can_visit_link(url))
        url = 'http://external.com/home'
        self.assertFalse(solution_one.can_visit_link(url))

    def test_should_respect_the_robots_txt_rules(self):
        rules = '''
        User-Agent: *
        Disallow: /login
        '''
        solution_one.RERP.parse(rules)
        url = 'http://test.com/login'
        self.assertFalse(solution_one.can_visit_link(url))
        url = 'http://test.com/logout'
        self.assertTrue(solution_one.can_visit_link(url))


if __name__ == '__main__':
    unittest.main(argv=sys.argv)
