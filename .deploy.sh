#!/bin/bash
pipenv run scrapy list | xargs -I {} pipenv run scrapy crawl {}
