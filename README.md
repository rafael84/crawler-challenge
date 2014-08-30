# crawler-challenge

## The Problem

Write a crawler that visits the web site epocacosmeticos.com.br and save into a .csv file the name
of the product, the page title and the page url for each product page[1] found; this file must
contain no duplicate entry.

It is allowed to use any framework or library wanted. The source code should be published and there
should be a README file that explains how to install and run the program.

[1] A product page is the one the contains information (name, price, availability, description,
etc) of one product only. The home page, search resuls or category are not considered product
pages.

This is a product page:
    http://www.epocacosmeticos.com.br/hypnose-eau-de-toilette-lancome-perfume-feminino/p

But this is not a product page:
    http://www.epocacosmeticos.com.br/cabelos

## Solution Two

This is a quite simple solution, based on sitemaps.

The web site to be crawled has sitemaps for all products. There were some broken links when crawler
ran for the first time.

The program runs sequentially, which leads to a very poor performance. On the other hand, this
means that we play nicely with the website, as we only make one request at a time.

### How to run the program

    ./crawler.py 
