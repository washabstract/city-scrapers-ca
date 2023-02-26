#!/bin/bash
echo "Running scrapers"
pipenv run scrapy list

# Assign variable to list of scrapers
SCRAPERS=$(pipenv run scrapy list)

# Loop through each scraper
for scraper in $SCRAPERS
do
    echo "Running $scraper"
    pipenv run scrapy crawl $scraper
done
