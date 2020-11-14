#!/usr/bin/env

"""
WildbowCrawler, written by J. Alex Ruble

A web-scraper for locally archiving Worm, Pact, and Twig.
"""

import os
import sys
import re
import unicodedata
import requests
import bs4

class Crawler():
    def __init__(self):
        self.hardcode_data()
        self.handle_arguments()
        self.init_counters()
        self.init_dir()
        self.init_replacement()

    def hardcode_data(self):
        self.stories = [
            'Worm',
            'Pact',
            'Twig',
        ]
        self.outputkeywords = [
            'single',
            'per-arc',
        ]
        self.urls = {
            'Worm': 'http://parahumans.wordpress.com/category/stories-arcs-1-10/arc-1-gestation/1-01/',
            'Pact': '',
            'Twig': '',
        }
        self.italicsstring = u'*'
        self.boldstring = u'**'
        self.underlinestring = u'_'

    def handle_arguments(self):
        args = sys.argv
        if len(args) != 5:
            print 'Wrong number of input arguments.'
            self.quit(True)
        story = args[1].capitalize()
        if story in self.stories:
            self.story = story
        else:
            print 'Invalid story.'
            self.quit(True)
        self.url = self.urls[story]
        output = args[2].lower()
        if output in self.outputkeywords:
            self.output = output
        else:
            print 'Invalid output keyword.'
            self.quit(True)
        self.arctag = args[3]
        self.chaptertag = args[4]

    def init_counters(self):
        self.previousarc = u''
        self.arc = u''
        self.arcnumber = 0
        self.chapternumber = 0

    def init_dir(self):
        self.path = os.path.dirname(__file__)
        print 'path: ' + `self.path`
        try:
            os.mkdir(os.path.join(self.path, self.story))
        except OSError:
            if not os.path.isdir(os.path.join(self.path, self.story)):
                raise
        self.storypath = os.path.join(self.path, self.story)

    def init_replacement(self):
        self.reps = {
            u'\xa0': u' ',
            u'\xbd': u'.5',
            u'\xc7': u'C',
            u'\xdc': u'U',
            u'\xe0': u'a',
            u'\xe1': u'a',
            u'\xe3': u'a',
            u'\xe4': u'a',
            u'\xe8': u'e',
            u'\xe9': u'e',
            u'\xea': u'e',
            u'\xeb': u'e',
            u'\xec': u'i',
            u'\xed': u'i',
            u'\xf2': u'o',
            u'\xf5': u'o',
            u'\xf6': u'o',
            u'\xf9': u'u',
            u'\xfa': u'u',
            u'\xfc': u'u',
            u'\u0101': u'a',
            u'\u0113': u'e',
            u'\u011b': u'e',
            u'\u012b': u'i',
            u'\u014d': u'o',
            u'\u016b': u'u',
            u'\u01ce': u'a',
            u'\u0302': u'',
            u'\u0304': u'',
            u'\u2013': u'-',
            u'\u2018': u'\'',
            u'\u2019': u'\'',
            u'\u201c': u'"',
            u'\u201d': u'"',
            u'\u2022': u'*',
            u'\u2026': u'...',
            u'\u25ba': u'->',
            u'\u25a0': u'---',
            u'\u263f': u'M',
            u'\u2666': u'*',
            u'\n': u'\n\n',
        }
        self.reps = dict((re.escape(key), value) for key, value in self.reps.iteritems())
        self.reppattern = re.compile('|'.join(self.reps.keys()))


    def run(self):
        self.running = True
        while self.running:
            self.get_soup()
            self.parse()
            self.get_text()
            self.write()
            self.get_next_url()

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
        if match is None:
            print 'No title found for URL {0!s}'.format(self.url)
            self.quit(True)
        self.title = self.format_string(match.string)
        print 'Got title: {0!s}'.format(self.title)

    def get_arc(self):
        arcregex = re.compile(r'(.*?):? (\d|e|End)')
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
        self.delimiters = self.content_tag.find_all(self.is_delimiter, recursive=False)
        if len(self.delimiters) != 2:
            print 'Delimiter problem: ' + `len(self.delimiters)`
            for d in self.delimiters:
                print d.prettify()
            self.quit(True)

    def is_delimiter(self, tag):
        has_last = tag.find('a', text=re.compile(r'Last Chapter'), recursive=False)
        has_next = tag.find('a', text=re.compile(r'Next Chapter'), recursive=False)
        return has_last or has_next

    def get_text(self):
        rawstring = u''
        for tag in self.content_tag.find_all('em'):
            if list(tag.children):
                list(tag.children)[0].insert_before(self.italicsstring)
                list(tag.children)[-1].insert_after(self.italicsstring)
        for tag in self.content_tag.find_all('strong'):
            if list(tag.children):
                list(tag.children)[0].insert_before(self.boldstring)
                list(tag.children)[-1].insert_after(self.boldstring)
        for tag in self.content_tag.find_all('span', attrs={'style': 'text-decoration-underline;'}):
            if list(tag.children):
                list(tag.children)[0].insert_before(self.underlinestring)
                list(tag.children)[-1].insert_after(self.underlinestring)
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
                self.quit(True)
        self.text = self.format_string(rawstring)

    def format_string(self, string):
        return self.reppattern.sub(lambda match: self.reps[re.escape(match.group(0))], string)

    def write(self):
        if self.output == 'single':
            self.filepath = os.path.join(self.storypath, self.story + '.txt')
            print 'Writing chapter {0} to file {1}'.format(self.title, self.filepath)
            if not hasattr(self, 'file'):
                self.file = open(self.filepath, 'w')
                self.file.write('{0}\nby Wildbow (J.C. McCrae)\n\n'.format(self.story))
            if self.arc != self.previousarc:
                self.file.write('{0}    {1!s}\n\n'.format(self.arctag, self.arc))
        elif self.output == 'per-arc':
            if self.previousarc != self.arc:
                self.close_file()
                self.filepath = os.path.join(self.storypath, '{0:d}_{1}.txt'.format(self.arcnumber, self.arc))
                self.file = open(self.filepath, 'w')
                if self.arcnumber == 1:
                    self.file.write('{0}\nby Wildbow (J.C. McCrae)\n\n'.format(self.story))
                self.file.write('{0}    {1}\n\n'.format(self.arctag, self.arc))
        self.file.write('{0}    {1}\n\n'.format(self.chaptertag, self.title))
        self.file.write('{0}\n\n'.format(self.text.encode('ascii', 'ignore')))

    def close_file(self):
        if hasattr(self, 'file'):
            #strip last two \n\n
            self.file.close()

    def get_next_url(self):
        url = self.delimiters[0].find('a', text=re.compile(r'Next Chapter'))
        if url:
            self.url = url['href']
        else:
            self.quit(False)

    def quit(self, error):
        self.close_file()
        self.running = False
        sys.exit('Aborting.' if error else 'Finished!')

if __name__ == '__main__':
    crawler = Crawler()
    crawler.run()
