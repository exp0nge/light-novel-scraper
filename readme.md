# light-novel-scrapper

## About

A scrapper tool to grab contents of chapters of a light novel and store them
as HTML files (and soon ePubs) to read later. The script utilizes
Readability to grab relevant text from a website.

## Usage

The following will grab all the chapters from 21 to 52:

    ls = Scrapper(title='Smartphone',
               start_chapter_number=31,
               end_chapter_number=53,
               url='http://raisingthedead.ninja/2015/10/06/smartphone-chapter-31/')          
    ls.chapters_walk()  # Grab all the HTML files
    ls.make_html_toc()  # Make a HTML table of contents file to use with calibre

## Requirements

Have the following installed with `pip`:

1. [beautifulsoup4](http://www.crummy.com/software/BeautifulSoup/)
1. [readability-lxml](https://github.com/buriy/python-readability)
