# crawler-challenge

## The Problem

Write a crawler that visits the web site `epocacosmeticos.com.br` and save into
a `.csv` file the name of the product, the page title and the page url for each
product page[1] found; this file must not contain duplicate entries.

It is allowed to use any framework or library wanted. The source code should be
published and there should be a README file that explains how to install and run
the program.

[1] A product page is the one that contains information (name, price,
availability, description, etc) of one product only. The home page, search
results or category are not considered product pages.

This is a product page:
    `http://www.epocacosmeticos.com.br/hypnose-eau-de-toilette-lancome-perfume-feminino/p`

But this is not a product page:
    `http://www.epocacosmeticos.com.br/cabelos`

## Prerequisites

First of all, make sure you have Python 2.7.6+ and PIP installed onto your box.

The code was tested under that specific Python version and may not be compatible
with older versions nor the 3.x.

After you have cloned this repository, cd into it and then perform the following
commands:

    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.pip


## Solution One

Based on a simple URL discovery algorithm, this solution actually navigates
through all internal links on the website, performing an additional data
extraction task whenever a product page is found. 

The program keeps track of urls to be visited into a `queue`; also, the urls
already visited are stored in a `set`, so each url is only visited one time.

As the program may encounter lots of urls to be visited until it finds all the
product pages, the work is done by green (fake) threads - Greenlet, managed by
the Gevent library. So, the program uses a lightweight concurrency model.

The job is performed by the following steps:

1. take an url from the queue
2. make a request to this url
3. mark it as visited
4. check whether the response is ok to be parsed
5. if the url corresponds to a product page, then extract data from it and save
   the data in the csv file
6. extract more urls from the current page and add them to the queue

This is repeated continuously until the queue is empty.


### How to run this solution

    $ ./solution_one.py 

The output csv file will be saved as `data/solution_one.csv`, and the logs can
be found at `logs/solution_one.log`.


### How to test this solution

There are a couple of tests implemented for functions `can_visit_link` and
`discover_links`. To execute the tests, simply run this command:

    $ ./test_solution_one.py -v

The `-v` is optional.

The output should be something like this:

    $ ./test_solution_one.py -v

    test_should_check_the_black_list (__main__.TestCanVisitLink) ... ok
    test_should_not_allow_external_links (__main__.TestCanVisitLink) ... ok
    test_should_not_allow_the_same_url_twice (__main__.TestCanVisitLink) ... ok
    test_should_respect_the_robots_txt_rules (__main__.TestCanVisitLink) ... ok
    test_should_add_allowed_urls_to_queue_and_discovered (__main__.TestDiscoverLinks) ... ok
    test_should_ignore_links_starting_with_hashtag (__main__.TestDiscoverLinks) ... ok
    test_should_ignore_links_without_href (__main__.TestDiscoverLinks) ... ok
    test_should_treat_relative_links_properly (__main__.TestDiscoverLinks) ... ok

    ----------------------------------------------------------------------
    Ran 8 tests in 0.007s

    OK

## Solution Two

This is a quite simple solution, based on sitemaps.

The web site to be crawled has sitemaps for all products. There were some broken
links when crawler ran for the first time, though.

The program runs sequentially, which leads to a very poor performance. On the
other hand, this means that we play nicely with the website, as we only make one
request at a time.

The logic then is pretty straightforward:

1. open the output filename
2. get the root sitemap
3. get the product sitemaps from the root sitemap
4. access each product url and take the required data from it, saving the data
   on the output file

### How to run this solution

    $ ./solution_two.py 

The output csv file will be saved as `data/solution_two.csv`, and the logs can
be found at `logs/solution_two.log`.
