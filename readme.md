# light-novel-scrapper

## About

A scrapper tool to grab contents of chapters of a light novel and store them
as HTML files (and soon ePubs) to read later. The script utilizes
Readability to grab relevant text from a website.

## Usage

The following will grab all the chapters from 21 to 52:

`chapters_walk(21, 52, 'start_url')`

## Requirements

Have the following installed with `pip`:

1. [beautifulsoup4](http://www.crummy.com/software/BeautifulSoup/)
1. [readability-lxml](https://github.com/buriy/python-readability)
