#!/bin/env python3

from bs4 import BeautifulSoup


with open("aio_test_scrape.html", "r") as f:
    bleh = f.read()

soup = BeautifulSoup(bleh, 'lxml')
desc = soup.select_one('.woocommerce-product-details__short-description')

print(desc)