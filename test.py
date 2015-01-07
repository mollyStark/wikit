# This is used to scrawl the wiki commons images .
# Write by molly according __init__py
# 2014/12/9

import os
import re
import urlparse
from datetime import datetime

from cola.core.urls import UrlPatterns, Url
from cola.core.parsers import Parser
from cola.core.opener import MechanizeOpener
from cola.core.errors import DependencyNotInstalledError
from cola.core.config import Config
from cola.job import Job

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise DependencyNotInstalledError('BeautifulSoup4')

try:
    from dateutil.parser import parse
except ImportError:
    raise DependencyNotInstalledError('python-dateutil')

try:
    from mongoengine import connect, DoesNotExist, \
                            Document, StringField, DateTimeField
except ImportError:
    raise DependencyNotInstalledError('mongoengine')


get_user_conf = lambda s: os.path.join(os.path.dirname(os.path.abspath(__file__)), s)
user_conf = get_user_conf('test.yaml')
if not os.path.exists(user_conf):
    user_conf = get_user_conf('wiki.yaml')
user_config = Config(user_conf)

starts = [start.url for start in user_config.job.starts]

mongo_host = user_config.job.mongo.host
mongo_port = user_config.job.mongo.port
db_name = user_config.job.db
connect(db_name, host=mongo_host, port=mongo_port)

class WikiImageDocument(Document):
    title = StringField()
    height = IntField()
    width = IntField()
    last_update = StringField()
    global_usages = WikiDocument()

class WikiDocument(Document):
    title = StringField()
    content = StringField()
    last_update = DateTimeField()

url_patterns = UrlPatterns(
    Url(r'^http://commons.wikimedia.org/wiki/File:\w+','wiki_file',WikiImgParser)
    Url(r'^http://commons.wikimedia.org/wiki/Category:\w+','wili_category',WikiCatoParser)
    #Url(r'^http://(zh|en).wikipedia.org/wiki/[^():|/]+$','wiki_page',WikiDocParser)
)

def get_job():
    return Job('wikicommons crawler',url_patterns,MechanizeOpener,starts,instances = user_config.job.instances,user_conf = user_config,debug = True)


#to support work on one computer
if __name__ == "__main__":
    from cola.worker.loader import load_job
    load_job(os.path.dirname(os.path.abspath(__file__)))

def WikiImgParser(Parser):
    def __init__(self,opener = None,url=None,**kw):
	super(WikiImgParser,self).__init__(opener=opener,url=url,**kw)

	if self.opener is None:
	    self.opener = MechanizeOpener()
	self.html_category_reg = re.compile(r'/wiki/Category:.*',re.DOTALL)
	self.html_filelink_reg = re.compile(r'src="//upload.wikimedia.*.JPG"',re.DOTALL)
	self.html_comment_reg = re.compile(r'<!--[^-]+-->',re.DOTALL)
	self.en_time_reg = re.compile(r'\d{1,2} [A-Z][a-z]{2,} \d{4} at \d{1,2}:\d{1,2}')
        self.zh_time_reg = re.compile(ur'\d{4}年\d{1,2}月\d{1,2}日 \(.+\) \d{1,2}:\d{1,2}')
        
    def parse(slef,url= None):
	url = url or self.url
	
	br = self.opener.browse_open(url)
	html = br.response().read()
	html = self.html_comment_reg.sub('',html)
	#subcategory = self.html_category_reg.findall(html)

	soup = BeautifulSoup(html)
	#if subcategory is None:
	title,width,height,last_update,global_usage = self._extractImg(soup)
	self.storeImgInfo(title,width,height,last_update,global_usage)
	self.storeImg()
	return []

    def _extractImg(self,soup):
	if soup.head is None:
	    return None,None,None,None,None
        
    	content = soup.find('div',attrs={'id':'file','class':'fullImageLink'})
	file_link = self.html_file_link.search(content)
	width = self.pic_width_reg.search(content)
	height = self.pic_height_reg.search(content)
	
	last_update_str = soup.find('li', attrs={'id': 'footer-info-lastmod'}).text
        last_update = None
        match_en_time = self.en_time_reg.search(last_update_str)
        if match_en_time:
            last_update = match_en_time.group()
            last_update = parse(last_update)
        match_zh_time = self.zh_time_reg.search(last_update_str)
        if match_zh_time:
            last_update = match_zh_time.group()
            last_update = re.sub(r'\([^\)]+\)\s', '', last_update)
            last_update = last_update.replace(u'年', '-').replace(u'月', '-').replace(u'日', '')
            last_update = parse(last_update)
        if last_update is None:
            last_update = datetime.now()

	golbal_usage_content = soup.find('div',attrs={'id':'mv-imagepage-section-globalusage'})
	tmp = BeautifulSoup(global_usage_content)

	doc_title = tmp.find('a',attrs={'class':'external'}).text
	doc_link = 
	
	return title,width,height,last_update,global_usage


    	title,content,last_update,lang = self._extractLink(soup)
	if title is None:
	    return []
    
	title = title + ' '+ lang
	self.storeLinks(title,content,last_update)
	
        
    def storeImg(self, title, width,height, last_update,global_usage):
        try:
            img = WikiImageDocument.objects.get(title=title)
            if last_update > img.last_update:
                img.width = width
		img.height = height
		img.global_usage = global_usage
                img.last_update = last_update
                img.update(upsert=True)
        except DoesNotExist:
            img = WikiImageDocument(title=title, height = height,width = width,global_usage=global_usage, last_update=last_update)
            img.save()

    def _extractImg(self,soup):
	if soup.head is None:
	    return None,None,None,None,None

	title = soup.head.title.text
	if '-' in title
	    title = title.split('-')[0].strip()
	content = soup.find


class WikiDocParser(Parser):
    def __init__(self, opener = None, url= None, **kw):
	super(WikiParser,self).__init__(opener=opener,url=url,**kw)

	if self.opener is None:
	    self.opener = MechanizeOpener()
	self.html_comment_reg = re.compile(r'<!--[^-]+-->',re.DOTALL)
	self.html_category_reg = re.compile(r'<a href=>')
	self.en_time_reg = re.compile(r'\d{1,2} [A-Z][a-z]{2,} \d{4} at \d{1,2}:\d{1,2}')
	self.zh_time_reg = re.compile(ur'\d{4}年\d{1,2}月\d{1,2}日 \(.+\) \d{1,2}:\d{1,2}')
        
    def storeUsage(self, title, content, last_update):
        try:
            doc = WikiDocument.objects.get(title=title)
            if last_update > doc.last_update:
                doc.content = content
                doc.last_update = last_update
                doc.update(upsert=True)
        except DoesNotExist:
            doc = WikiDocument(title=title, content=content, last_update=last_update)
            doc.save()
        
       def _extractDoc(self,soup):
	if soup.head is None:
	    return None,None,None
    	
    	title = soup.head.title.text
	if '-' in title:
	    title = title.split('-')[0].strip()


