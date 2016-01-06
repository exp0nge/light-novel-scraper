import urllib2
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from readability.readability import Document
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
    
