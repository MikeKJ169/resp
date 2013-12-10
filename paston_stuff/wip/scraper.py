#!/usr/bin/env python

from HTMLParser import HTMLParser
from urllib2 import urlopen
from paston_stuff.utils.spider import Spider
import re, getopt, sys, os

# Define where the image path is supposed to be
# TODO: get this from settings.py


# Define the parser. It is very basic at the moment it strips all 
# tags other than these:
#
# valid_tags = ('b', 'u', 'i', 'br', 'h1', 'h2', 'h3', 'h4', 'img', 'form', 'input')
# 
# and tries to clean up the code a bit. It currently does some silly things
# with spaces that needs fixing.
# TODO: make this work a bit better as it is a bit of bodge at the moment

class StrippingParser(HTMLParser):
	valid_tags = ('b', 'u', 'i', 'br', 'h1', 'h2', 'h3', 'h4', 'img', 'table', 'tr', 'td', 'ol', 'ul', 'li', 'title', 'form', 'input')
	result = ''
	title = ''
	in_title = False
	
	def handle_starttag(self, tag, attr):
		if tag in self.valid_tags:
			if tag == 'title':
				self.in_title = True
			self.result = self.result + '<' + tag
			for k, v in attr:
				if k == 'src' and tag == 'img':
					v = re.sub(r'^.*/(.*)$', r'/media/images/\1', v)
				self.result = '%s %s="%s"' % (self.result, k, v)
				
			if tag == 'br' or tag == 'img':
				self.result += ' />'
			else:
				self.result += '>'
							
	def handle_endtag(self, tag):
		if tag in self.valid_tags:
			if tag == 'title':
				self.in_title = False
			self.result = self.result + "</" + tag + ">"
			
	def handle_data(self, data):
		if self.in_title == True:
			self.title += data
#		data = re.sub('\s{2,150}', r'', data)
#		data = re.sub('\n{2,100}', r'', data)
		self.result += data
			
	def getcontent(self):
		return self.result
		
	def get_title(self):
		return self.title

def worker(SITENAME, IMAGE_PATH):
	s = Spider(SITENAME)

	# Loop through each url and download all of the images
#	for url in s.weburls():
#		if url.endswith('gif') or url.endswith('jpg'):
#			image_name = re.sub(r'^.*/(.*)$', r'\1', url)
#			print 'Getting file: ' + image_name
#			open(IMAGE_PATH + image_name, "w").write(urlopen(url).read())
		
	# Loop through each webpage url and scrape the data from it into a SmartPage
	uniq_num = 0
	for url in s.weburls():
		if url.endswith('html') or url.endswith('htm'):	
			pageparser = StrippingParser()
			page_name = re.sub(r'^.*/(.*)$', r'\1', url)
			page_name = re.sub('^(.*)\..*$', r'\1', page_name)
			pageparser.feed(urlopen(url).read())
			page_title = pageparser.get_title()
			print page_name + " " + page_title
			if page_name.startswith('index') or page_name.startswith('home') or page_name.startswith('default') or page_name == 'index':
				page_title = 'home'
			try:
		 		SmartPage.objects.get(slug=page_name)
			except ObjectDoesNotExist:
				pass
			else:
				page_title = page_title + uniq_num
			s = SmartPage(name=page_title, slug=page_name, editor_timestamp='', editor_uniqid='', content=pageparser.getcontent())
			s.save()
			
			print 'Scraping url ' + url + ' as ' + page_title
			s.categories.add(Category.objects.get(pk=1))
			s.save()
			
			uniq_num = uniq_num + 1
			
def usage():
    print """    Usage:

    scraper.py --site=www.yourdomain.tld --settings=projectname.settings
"""
		
if __name__ == '__main__':
	try:
		opts, remargs = getopt.getopt(sys.argv[1:], '', ['help','site=','settings=',])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	
	sitename = ''
	settings = ''
	for opt, value in opts:
		if opt == '--site':
			sitename = value
		elif opt == '--settings':
			settings = value
			
	if sitename and settings:
		if not sitename.startswith('http://'):
			sitename = 'http://'+sitename
		os.environ['DJANGO_SETTINGS_MODULE'] = settings
		from smartpages.models import SmartPage, Category
		from django.core.exceptions import ObjectDoesNotExist
		from django.conf import settings
		IMAGE_PATH = settings.MEDIA_ROOT + "images/"
		worker(sitename, IMAGE_PATH)
	else:
		usage()
