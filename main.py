# downloadXKCD.py

import os
import sys
import re
import unicodedata
import requests
import bs4

class Crawler():
    def __init__(self):
        self.url = 'http://parahumans.wordpress.com/category/stories-arcs-1-10/arc-1-gestation/1-01/'
        self.italicsstring = '*'
        self.output = 'per-arc' # 'single' or 'per-arc'
        self.arctag = '[ARC]'
        self.chaptertag = '[CHAPTER]'
        self.previousarc = u''
        self.arc = u''
        self.arcnumber = 0
        self.chapternumber = 0
        self.story = 'Worm'
        self.init_dir()
        
    def init_dir(self):
        self.path = os.path.dirname(__file__)
        print 'path: ' + `self.path`
        try:
            os.mkdir(os.path.join(self.path, self.story))
        except OSError:
            if not os.path.isdir(os.path.join(self.path, self.story)):
                raise
        self.storypath = os.path.join(self.path, self.story)

    def run(self):
        self.running = True
        while self.running:
            self.get_soup()
            self.parse()
            self.get_text()
            self.write()
            self.get_next_url()
        self.quit()
        
    def get_soup(self):
        print 'Accessing URL {0!s}...'.format(self.format_string(self.url))
        res = requests.get(self.url)
        res.raise_for_status()
        self.soup = bs4.BeautifulSoup(res.text, 'html.parser')

    def parse(self):
        self.get_title()
        self.get_arc()
        self.get_content()
        
    def get_title(self):
        match = self.soup.find(attrs={'class': 'entry-title'})
        if match == None:
            print 'No title found for URL {0!s}'.format(self.url)
            self.quit()
        self.title = self.format_string(match.string)
        print 'Got title: {0!s}'.format(self.title)

    def get_arc(self):
        arcregex = re.compile(r'(.*) (\d|e)')
        name = arcregex.search(self.title).group(1)
        self.previousarc = self.arc
        self.arc = name if name != 'Interlude' else self.arc
        if self.previousarc != self.arc:
            self.chapternumber = 0
            self.arcnumber += 1
            print 'Reached new arc "{0!s}"'.format(self.arc)
        self.chapternumber += 1

    def get_content(self):
        self.content_tag = self.soup.find(attrs={'class': 'entry-content'})
        self.delimiters = self.content_tag.find_all(self.is_delimiter)
        if len(self.delimiters) != 2:
            print 'Delimiter problem'
            self.quit()

    def is_delimiter(self, tag):
        has_previous = tag.find('a', text=re.compile(r'Last Chapter'), recursive=False)
        has_next = tag.find('a', text=re.compile(r'Next Chapter'), recursive=False)
        return has_previous or has_next

    def get_text(self):
        rawstring = u''
        for tag in self.content_tag.find_all('em'):
            if list(tag.children):
                list(tag.children)[0].insert_before(self.italicsstring)
                list(tag.children)[-1].insert_after(self.italicsstring)
        writing = False
        for element in self.content_tag.children:
            if isinstance(element, bs4.Tag):
                if element in self.delimiters:
                    writing = not writing
                elif writing:
                    rawstring += element.text
            elif isinstance(element, bs4.NavigableString):
                if writing:
                    rawstring += unicode(element)
            else:
                print 'Unknown element type ' + `type(element)` + '.'
                self.quit()
        self.text = self.format_string(rawstring)
        
    def format_string(self, string):
        string = string.replace(u'\xa0', u' ')
        string = string.replace(u'\xbd', u'.5')
        string = string.replace(u'\xdc', u'U')
        string = string.replace(u'\u2013', u'-')
        string = string.replace(u'\u2018', u'\'')
        string = string.replace(u'\u2019', u'\'')
        string = string.replace(u'\u201c', u'"')
        string = string.replace(u'\u201d', u'"')
        string = string.replace(u'\u2026', u'...')
        string = string.replace(u'\u25a0', u'---')
        string = string.replace(u'\n', u'\n\n')
        string = string.strip()
        return string
        
    def write(self):
        if self.output == 'single':
            self.filepath = os.path.join(self.storypath, self.story + '.txt')
            print 'Writing chapter {0!s} to file {1!s}'.format(self.title, self.filepath)
            if not hasattr(self, 'file'):
                self.file = open(self.filepath, 'w')
                self.file.write('{0!s}\nby Wildbow (J.C. McCrae)\n\n'.format(self.story))
            if self.arc != self.previousarc:
                self.file.write('{0!s}    {1!s}\n\n'.format(self.arctag, self.arc))
        elif self.output == 'per-arc':
            if self.previousarc != self.arc:
                self.close_file()
                self.filepath = os.path.join(self.storypath, '{0:d}_{1!s}.txt'.format(self.arcnumber, self.arc))
                self.file = open(self.filepath, 'w')
                self.file.write('{0!s}    {1!s}\n\n'.format(self.arctag, self.arc))
        self.file.write('{0!s}    {1!s}\n\n'.format(self.chaptertag, self.title))
        self.file.write('{0!s}\n\n'.format(self.text))
    
    def close_file(self):
        if hasattr(self, 'file'):
            #strip last two \n\n
            self.file.close()
    
    def get_next_url(self):
        url = self.delimiters[0].find('a', text=re.compile(r'Next Chapter'))
        if url:
            self.url = url['href']
        else:
            self.quit()
        
    def quit(self):
        self.close_file()
        self.running = False
    
if __name__ == '__main__':
    crawler = Crawler()
    crawler.run()
    pass
        
"""
while not url.endswith('#'):
    # Download the page
    print 'Downloading page %s...' % url
    res = requests.get(url)
    res.raise_for_status()
    
    soup = bs4.BeautifulSoup(res.text)
    
    # Find url
    comicElem = soup.select('#comic img')
    if comicElem == []:
        print 'Could not find comic image.'
    else:
        try:
            comicUrl = 'http:' + comicElem[0].get('src')
            # Download the image
            print 'Downloading image %s...' % (comicUrl)
            res = requests.get(comicUrl)
            res.raise_for_status()
        except requests.exceptions.MissingSchema:
            # Skip this comic
            prevLink = soup.select('a[rel="prev"')[0]
            url = 'http://xkcd.com' + prevLink.get('href')
            continue
    
       # Save the image to ./xkcd
        imageFile = open(os.path.join('xkcd', os.path.basename(comicUrl)), 'wb')
        for chunk in res.iter_content(100000):
            imageFile.write(chunk)
        imageFile.close()

    # Get the prev button's url
    prevLink = soup.select('a[rel="prev"]')[0]
    url = 'https://xkcd.com' + prevLink.get('href')
      
print 'Done.'
"""
