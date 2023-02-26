#!/bin/bash
echo "Running scrapers"
pipenv run scrapy list

# Assign variable to list of scrapers
SCRAPERS=$(pipenv run scrapy list)
echo $SCRAPERS

# create a list of scrapers that failed
FAILED_SCRAPERS=()

# Loop through each scraper
for scraper in $SCRAPERS
do
    echo "Running $scraper"
    pipenv run scrapy crawl $scraper

    # check if the previous command failed and add the scraper to the list of failed scrapers
    if [ $? -ne 0 ]; then
        FAILED_SCRAPERS+=($scraper)
    fi
done

echo "Scrapers that failed: ${FAILED_SCRAPERS[@]}"
