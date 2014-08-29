#!/usr/bin/env python
import logging
import urllib2

from StringIO import StringIO
import gzip

logging.basicConfig(level=logging.INFO)

ROOT_URL = 'http://epocacosmeticos.com.br'


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


if __name__ == '__main__':
    logging.info('crawler has been started')
    # todo
    logging.info('crawler finished')
