import urllib2
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from readability.readability import Document
from ebooklib import epub
from bs4 import BeautifulSoup

header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}

def visit_url(url):
    """
    http://stackoverflow.com/questions/7933417/how-do-i-set-headers-using-pythons-urllib
    """
    request = urllib2.Request(url, None, header)
    return urllib2.urlopen(request).read()

def strip_chapter(html):
    doc = Document(html)
    return (doc.short_title(),
           str(doc.summary()).replace('<html>', '<html><head><meta charset="utf-8"></ha'))

def find_from_toc(chapter_number, url):
    chapter_number = str(chapter_number)
    soup = BeautifulSoup(visit_url(url), 'html.parser')
    chapter = 'chapter ' + chapter_number
    for link in soup.find_all('a'):
        if chapter in link.text.lower():
            return link.get('href')



def chapters_walk(start_chapter_number, end_chapter_number, url):
    if start_chapter_number > end_chapter_number:
        print  'finished'
        return

    print 'Fetching chapter ' + str(start_chapter_number)
    # book = epub.EpubBook()
    # book.set_title(title)
    # book.add_author(start_url)
    # chapter_contents = strip_chapter(visit_url(start_url))
    # chapter = epub.EpubHtml(title=chapter_contents[0],
    #                         content=chapter_contents[1],
    #                         file_name='chap_01.xhtml')
    # book.add_item(chapter)
    #
    # book.add_item(epub.EpubNcx())
    # book.add_item(epub.EpubNav())
    # # define CSS style
    # style = 'BODY {color: white;}'
    # nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    #
    # # add CSS file
    # book.add_item(nav_css)
    # book.spine = ['nav', chapter]
    # with open('test.html', 'w+') as f:
    #     f.write(chapter_contents[1])
    # epub.write_epub('test.epub', book, {})

    # Start on initial url

    html = visit_url(url)
    chapter = strip_chapter(html)
    with open(str(start_chapter_number) + '.html', 'w+') as f:
        f.write(chapter[1])

    # Start walking
    soup = BeautifulSoup(html, 'html.parser')

    toc = ''
    # Find next chapter
    for link in soup.find_all('a'):
        if 'next chapter' in link.text.lower():
            return chapters_walk(start_chapter_number + 1, end_chapter_number, link.get('href'))
        if 'table of contents' in link.text.lower():
            toc = link.get('href')
    return chapters_walk(start_chapter_number + 1, end_chapter_number, find_from_toc(start_chapter_number + 1, toc))

if __name__ == '__main__':
    chapters_walk(21, 52, 'http://raisingthedead.ninja/2015/10/01/smartphone-chapter-21/')
