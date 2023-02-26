#!/bin/bash
echo "Running scrapers"
pipenv run scrapy list
pipenv run scrapy list | xargs -I {} pipenv run scrapy crawl {}
