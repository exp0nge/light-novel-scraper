# coding=utf-8
import urllib2
import sys
import os
import datetime
import zipfile
import io
from collections import OrderedDict
import re
from tld import get_tld

from readability.readability import Document
from bs4 import BeautifulSoup
from ebooklib import epub
import simplejson

from webapp import db, celery
from models import Chapter, NovelInfo

reload(sys)
sys.setdefaultencoding('utf-8')  # Needed fore websites that use Unicode


import httplib  # or http.client if you're on Python 3

httplib._MAXHEADERS = 1000

class TableOfContentsError(Exception):
    """
    Useful to raise if TOC not found
    """
    pass


class LightScrapAPI(object):
    """
    Scrapper object which can walk through chapters and grab relevant content
    """

    def __init__(self, title, start_chapter_number, end_chapter_number, url, task_id, celery_task, header=None):
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
        self.domain = get_tld(self.start_url)
        self.chapter_model = Chapter
        self.db = db
        self.main_content_div = 'entry-content'
        self.toc = OrderedDict()
        self.id = task_id
        self.celery_task = celery_task
        if header is None:
            self.header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) '
                                         'Gecko/20091102 Firefox/3.5.5'}
        else:
            self.header = header

    def visit_url(self, url):
        """
        http://stackoverflow.com/questions/7933417/how-do-i-set-headers-using-pythons-urllib
        :param url: URL to visit
        :return: str
        """
        if self.domain not in url:
            url = 'http://' + self.domain + url
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
        for chapter_number in self.toc.keys():
            toc += chapter_html.format(chapter_number)
        toc += '</p></body></html>'
        return toc

    def find_toc(self):
        """
        Locate, from the start URL, and return URL of table of contents
        :return:
        """
        soup = BeautifulSoup(self.visit_url(self.start_url), 'html.parser')
        for link in soup.find_all('a'):
            if 'table of contents' in link.text.lower():
                return link.get('href')
        raise TableOfContentsError('Table of contents not found, please specify it.')

    def chapters_walk(self):
        """
        Recursive method to walk from of URL to end
        :return:
        """
        if self.start_chapter_number > self.end_chapter_number:
            return

        self.toc[self.start_chapter_number] = self.url

        if self.url is None:
            return

        html = self.visit_url(self.url)
        chapter = self.strip_chapter(html)
        if len(chapter[1]) < 3000:
            return
        # update celery on progress
        self.celery_task.update_state(state='PROGRESS',
                                      meta={'current_chapter': self.start_chapter_number,
                                            'end_chapter': self.end_chapter_number})
        # save to database
        chapter_db = self.chapter_model(task=self.id,
                                        content=simplejson.dumps(chapter[1], cls=simplejson.encoder.JSONEncoderForHTML),
                                        chapter_number=int(self.start_chapter_number),
                                        url=self.url)

        self.db.session.add(chapter_db)
        self.db.session.commit()

        # Continue walking
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
        return self.chapters_walk()

    def toc_walk(self, toc_url):
        """
        Grabs links from table of contents
        :param toc_url: str
        :return:
        """
        self.toc = OrderedDict()

        # Find all the links
        watered_soup = BeautifulSoup(self.visit_url(toc_url), 'html.parser')
        for i in range(self.start_chapter_number, self.end_chapter_number + 1):
            self.toc[i] = None
        chapter_regex = re.compile(r'[0-9]*(c|C)hapter(\s|\S)(?P<chap_no>[0-9]*)')
        for link in watered_soup.find_all('a'):
            if 'chapter' in link.text.lower():
                found = chapter_regex.search(str(link.text))
                if found is not None:
                    found = found.group('chap_no')
                    if found and int(found) in self.toc.keys():
                        self.toc[int(found)] = link.get('href')

        for key, link in self.toc.items():
            # update celery on progress
            self.celery_task.update_state(state='PROGRESS',
                                          meta={'current_chapter': key,
                                                'end_chapter': self.end_chapter_number})
            content = self.strip_chapter(self.visit_url(link))
            chapter_db = self.chapter_model(task=self.id,
                                            content=simplejson.dumps(content[1],
                                                                     cls=simplejson.encoder.JSONEncoderForHTML),
                                            chapter_number=key,
                                            url=link)

            self.db.session.add(chapter_db)
            self.db.session.commit()


def add_novel_info(self, title, start, end, url):
    novel = NovelInfo(task=self.request.id,
                      start=start,
                      end=end,
                      title=title,
                      start_url=url,
                      request_time=datetime.datetime.now())

    db.session.add(novel)
    db.session.commit()


@celery.task(bind=True)
def chapters_walk_task(self, title, start, end, url):
    add_novel_info(self, title, start, end, url)
    light_task = LightScrapAPI(title=title,
                               start_chapter_number=start,
                               end_chapter_number=end,
                               url=url,
                               task_id=self.request.id,
                               celery_task=self)
    light_task.chapters_walk()


@celery.task(bind=True)
def toc_walk_task(self, title, start, end, url):
    add_novel_info(self, title, start, end, url)
    light_task = LightScrapAPI(title=title,
                               start_chapter_number=start,
                               end_chapter_number=end,
                               url=url,
                               task_id=self.request.id,
                               celery_task=self)
    light_task.toc_walk(url)


@celery.task()
def generate_epub(task_id, epub_path):
    """
        Generates a ePub with contents from the chapters_walk()
        :return:
    """
    toc_chapters = (Chapter.query.filter(Chapter.task == task_id)).order_by(Chapter.chapter_number)
    novel = NovelInfo.query.get(task_id)
    toc = OrderedDict()
    for chapter in toc_chapters:
        toc[chapter.chapter_number] = chapter.content
    title = novel.title
    book = epub.EpubBook()
    book.set_title(title)
    chapters = []
    for chapter_number, content in toc.items():
        chapter = epub.EpubHtml(title='Chapter ' + str(chapter_number),
                                file_name=str(chapter_number) + '.xhtml',
                                content=simplejson.loads(content))
        book.add_item(chapter)
        chapters.append(chapter)

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav']
    for chapter in chapters:
        book.spine.append(chapter)

    epub.write_epub(os.path.join(epub_path, task_id + '.epub'), book, {})
    return 'Success, chapters collected: ' + str(len(toc.keys()))


def generate_zip(task_id):
    """
    http://stackoverflow.com/questions/27337013/how-to-send-zip-files-in-the-python-flask-framework
    :param task_id: str
    :return: binary
    """
    # TODO: Add TOC
    chapters = Chapter.query.filter(Chapter.task == task_id)
    novel = NovelInfo.query.get(task_id)
    mem_file = io.BytesIO()
    with zipfile.ZipFile(mem_file, 'w') as zip_f:
        for chapter in chapters:
            data = zipfile.ZipInfo(str(chapter.chapter_number) + '.html')
            data.compress_type = zipfile.ZIP_DEFLATED
            zip_f.writestr(data, simplejson.loads(chapter.content))
    mem_file.seek(0)
    return mem_file, novel.title
