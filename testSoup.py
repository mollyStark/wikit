import os
import urllib2
import re
import urlparse
from bs4 import BeautifulSoup
from cola.core.opener import MechanizeOpener

url = 'http://commons.wikimedia.org/wiki/File:Aerial_View_of_Trout_Lake.JPG'
#url = 'http://commons.wikimedia.org/wiki/File:Capturing_the_rain_water_falling_from_roof.jpg'
br = MechanizeOpener().browse_open(url)
html = br.response().read()
#print html
soup = BeautifulSoup(html)
def saveImg(picurl):
	local_path = '/data/test/'
	names = picurl.split('/')
	picname = names[-1]
	print picname
	#name = re.match(pattern,picurl)
	#print name
	print 'downing',picurl
	#filename = local_path +  name.group()
	filename = local_path +  picname
	print filename
#print picurl
	try:
		response = urllib2.urlopen(picurl,timeout=10)
		cont = response.read()
	except urllib2.URLError,e:
		print e.reason
#	cont = MechanizeOpener().browse_open(picurl).read()

#	pattern = r'\d+[^/]+.JPG'
	f = open(filename,'w+')
	f.write(cont)
	f.close
	response.close()
if soup.head is not None:

	contents = soup.findAll('a',attrs={'class':'external'})
	for content in contents:
		print content.string
		link = content['href'].strip('//')

	#files = soup.findAll('div',attrs={'id':'file','class':'fullImageLink'})
	files = soup.findAll('img')
	#tmp = BeautifulSoap(files)
	#imgs = tmp.findAll('img')
	
	for img in files:
	#	print img['width']
		link= 'http:' + img['src']
		print link
		saveImg(link)





