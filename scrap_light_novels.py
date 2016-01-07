# coding=utf-8
import urllib2
import sys
import os

from readability.readability import Document
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')  # Needed fore websites that use Unicode


class Scrapper(object):
    """
    Scrapper object which can walk through chapters and grab relevant content
    """

    def __init__(self, title, start_chapter_number, end_chapter_number, url, header=None):
        """
        Instantiates the scrapper with the relevant information like the start URL (url) and how far to walk for
        all the chapters (end_chapter_number)
        :param title: str
        :param start_chapter_number: int
        :param end_chapter_number: int
        :param url: str
        :param header: dict
        :return:
        """
        self.title = title
        self.start_chapter_number = int(start_chapter_number)
        self.end_chapter_number = int(end_chapter_number)
        self.start_url = self.url = url
        self.main_content_div = 'entry-content'
        self.toc = []
        if header is None:
            self.header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) '
                                         'Gecko/20091102 Firefox/3.5.5'}
        else:
            self.header = header
        if not os.path.exists(self.title):
            os.makedirs(title)

    def visit_url(self, url):
        """
        http://stackoverflow.com/questions/7933417/how-do-i-set-headers-using-pythons-urllib
        :param url: URL to visit
        :return: str
        """
        request = urllib2.Request(url=url, headers=self.header)
        return urllib2.urlopen(request).read()

    def strip_chapter(self, html):
        """
        Strips chapter and gets relevant HTML using Readability
        :param html: str
        :return:
        """
        doc = Document(html)
        if len(doc.summary()) <= 20:
            print 'This page has errors, returning entry-content div raw HTML.'
            content = str(BeautifulSoup(html, 'html.parser').find_all('div', class_=self.main_content_div)[0])
            content = '<html><head><meta charset="utf-8"></head>' + content + '</html>'
            return doc.short_title(), content

        return (doc.short_title(),
                str(doc.summary()).replace('<html>', '<html><head><meta charset="utf-8"></head>'))

    def find_from_toc(self, chapter_number, url):
        """
        Grabs link from table of contents provided the chapter number and TOC URL
        :param chapter_number: int
        :param url: str
        :return:
        """
        chapter_number = str(chapter_number)
        soup = BeautifulSoup(self.visit_url(url), 'html.parser')
        chapter = 'chapter ' + chapter_number
        for link in soup.find_all('a'):
            if chapter in link.text.lower():
                return link.get('href')

    def make_html_toc(self):
        """
        Generates a HTML table of contents (to use with Calibre)
        :return: str
        """
        toc = """<html><html><body><h1>Table of Contents</h1>
        <p style="text-indent:0pt">"""
        chapter_html = '<a href="{0}.html">Chapter {0}</a><br/>'
        for chapter_number in self.toc:
            toc += chapter_html.format(chapter_number)
        toc += '</p></body></html>'
        with open(os.path.join(self.title, self.title + '-toc.html'), 'w+') as f:
            f.write(toc)
        return toc

    def chapters_walk(self):
        """
        Recursive method to walk from of URL to end
        :return:
        """
        if self.start_chapter_number > self.end_chapter_number:
            return

        self.toc.append(self.start_chapter_number)

        print 'Fetching chapter ' + str(self.start_chapter_number)

        html = self.visit_url(self.url)
        chapter = self.strip_chapter(html)
        with open(os.path.join(self.title, str(self.start_chapter_number) + '.html'), 'w+') as f:
            f.write(chapter[1])

        # Start walking
        soup = BeautifulSoup(html, 'html.parser')

        toc = ''
        # Find next chapter
        for link in soup.find_all('a'):
            if 'next chapter' in link.text.lower():
                self.start_chapter_number += 1
                self.url = link.get('href')
                return self.chapters_walk()
            if 'table of contents' in link.text.lower():
                toc = link.get('href')
        self.start_chapter_number += 1
        self.url = self.find_from_toc(self.start_chapter_number, toc)
        return self.chapters_walk()


if __name__ == '__main__':
    ls = Scrapper(title='Smartphone',
                  start_chapter_number=31,
                  end_chapter_number=53,
                  url='http://raisingthedead.ninja/2015/10/06/smartphone-chapter-31/')
    ls.chapters_walk()
    ls.make_html_toc()
