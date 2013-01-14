#!/usr/bin/python
# -*- encoding: utf-8 -*-

__author__ = "Peter Nguyen"
__version__ = "3.0 beta 2"

import urllib
import urllib2
import re
import httplib
import sys
import os
import time
import getopt
import random
import thread
from xml.etree import ElementTree
from urlparse import urlparse
from subprocess import call

hdrs = {
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0',
	'Accept-Language':'en-US,en;q=0.5',
	'Cache-Control': 'max-age=0',
	'Accept-Encoding': 'gzip, deflate, sdch',
	'Connection': 'keep-alive'
}

def show_process(proc_name,bytes_write,file_len):
	current = 0
	if(current < 100):
		current = (float(bytes_write)/float(file_len))*100
		output='\r --> %s [' % proc_name
		for i in range(1,int(current/2)+1):
			output+='#'
		for i in range(1,int((100-current)/2)+1):
			output+=' '
		if(current < 100):
			end_str = '] '+'{0:.2f}'.format(current)+'%'
		else:
			end_str = '] 100%|Done'
		output+=end_str
		sys.stdout.write(output)
	sys.stdout.flush()

def basic_download(url,outfile=''):
	req = urllib2.Request(url, headers=hdrs)
	n = urllib2.urlopen(req)
	file_len = int(n.info().getheaders('content-length')[0])
	file_type = n.info().getheaders('content-type')[0]
	file_type = file_type[len(file_type)-3:len(file_type)]
	
	if(os.path.exists(outfile) and os.path.getsize(outfile) == file_len):
		return 0
	if(not outfile):
		outfile+=os.getcwd()+'outfile'+'.'+file_type
	fw = open(outfile,'wb')
	sum_byte=0
	start = time.time()
	while True:
		show_process(outfile,sum_byte,file_len)
		bs = 1024*random.randint(10,256)
		data = n.read(bs)
		sum_byte+=len(data)
		fw.write(data)
		if(not data):
			break
	end = time.time()
	print '\n--> Total : %f ms' % (end-start)
	fw.close()
	n.close()
	return 1
      
def http(method,url,headers='',params='',):
        url_parse = urlparse(url)
        host      = url_parse[1]
        path      = url_parse[2]
        query     = url_parse[4]
        http      = httplib.HTTPConnection(host)
        if method=='GET':
                http.request(method,path+'?'+query)
        elif method =='POST':
                http.request(method,path,params,headers)
        res       = http.getresponse()
        result    = res.read()
        http.close()
        return result

class Mp3Zing :
	def __init__ (self,url):
		self.url=url
		self.name_song=[]
		self.artist_name=[]
		self.link_song=[]
		self.ext=[]
		data=urllib.urlopen(self.url)
		for line in data.read().split('\n'):
			try:
				_rem=re.search(r'xmlURL=(.+?)&',line)
				self.xmllink = _rem.group(1)
			except AttributeError:
				pass
		
	def xml_get_data(self):
		xml=urllib.urlopen(self.xmllink)
		xml_parse=ElementTree.parse(xml)   
		
		for name in xml_parse.findall('.//title'):
			self.name_song.append(unicode(name.text))
		for artist in xml_parse.findall('.//performer'):
			self.artist_name.append(unicode(artist.text))
		if(not xml_parse.findall('.//f480')):
			for link in xml_parse.findall('.//source'):
				self.link_song.append(unicode(link.text))
		else:
			for link in xml_parse.findall('.//f480'):
				self.link_song.append(unicode(link.text))
		
		for item in self.link_song:
			ext = item[item.rfind('.'):len(item)]
			self.ext.append(ext)
      
class NhacCuaTui:
	def __init__(self,url):
		self.name_song=[]
		self.artist_name=[]
		self.link_song=[]
		self.ext = []
		
		data = urllib.urlopen(url)

		for line in data.read().split('\n'):
			try:
				_re = re.search(r'file=(.+?)"',line)
				playlist = _re.group(1)
				break
			except AttributeError:
				pass
		      
		self.result = http('GET',playlist,hdrs)
	  
	def xml_get_data(self):
		self.name_song = re.findall(r'<title><!\[CDATA\[(.+?)\]\]>',self.result)
		self.link_song = re.findall(r'<location><!\[CDATA\[(.+?)\]\]>',self.result)
		self.artist_name = re.findall(r'<creator><!\[CDATA\[(.+?)\]\]>',self.result)
		  
		for item in self.link_song:
			ext = item[item.rfind('.'):len(item)]
			self.ext.append(ext)

class NhacSo:
	def __init__(self,url):
		self.name_song=[]
		self.artist_name=[]
		self.link_song=[]
		self.ext = []
		
		data = urllib.urlopen(url)
		
		_re = re.findall(r'xmlPath=(.+?)&',data.read())
		if _re:
			self.xml = _re[0]
		
	def xml_get_data(self):
		data = urllib.urlopen(self.xml)
		
		response = data.read()
		
		self.name_song = re.findall(r'\<name\>\<!\[CDATA\[(.+?)\]\]\>\<\/name\>',response)
		self.artist_name = re.findall(r'\<artist\>\<!\[CDATA\[(.+?)\]\]\>\<\/artist\>',response)
		self.link_song = re.findall(r'\<mp3link\>\<!\[CDATA\[(.+?)\]\]\>\<\/mp3link\>',response)

		for item in self.link_song:
			ext = item[item.rfind('.'):len(item)]
			self.ext.append(ext)

def filter_link_mp3(link):
	return urlparse(link)[1]  
  
def downloader(link_song,name_song,artist_name,path,ext,tool_download=None):
	
	mp3file_list = []
	
	if not os.path.isdir(path):
		os.mkdir(path)
	for item in range(len(link_song)):
		name_song[item]+=' - '+artist_name[item]+ext[item]
		if(path[len(path)-1] != '/'):
			path+='/'
		mp3file_list.append(path+name_song[item])

	if(tool_download):
		if(tool_download == 'wget'):
			flag='-O'
		elif(tool_download == 'axel'):
			flag='-o'
		
		for item in range(len(link_song)):      
			download=[tool_download]
			download.append(link_song[item])
			download.append(flag)
			download.append(mp3file_list[item])
			call(download)
	else:
		for item in range(len(link_song)):
			basic_download(link_song[item],mp3file_list[item])   

def usage():
	print 'Usage ./%s -s <path> -l <link> (-t wget option)' % sys.argv[0]

def help():
	print '''
	-t|--tool : axel,wget
	-l|--link : url link list
	-s|--save : path
	-e|--extract : path
	-v|--version : version
	-h|--help : help
	
	* If using option -e, this tool doesn't download files, instead, extracting link file to file text'
	'''
def main():
	support_tools = ['wget','axel']
	tool = None
	link = []
	save = os.getcwd()
	extract = ''
	try:
		opts,args = getopt.getopt(sys.argv[1:],'t:l:s:e:vh',['tool','link','save','extract','version','help'])
	except getopt.GetoptError as err:
		usage()
		print str(err)
		sys.exit(1)
	for option,variable in opts:
		if option in ('-t','--tool'):
			if(variable in support_tools):
				tool=variable
			else:
				print 'Tool %s doesn\'t support' % variable
				sys.exit(1)
		elif option in ('-l','--link'):
			link = variable.split(' ')
		elif option in ('-s','--save'):
			save = os.path.expanduser(variable)
		elif option in ('-e','--extract'):
			extract = os.path.expanduser(variable)
		elif option in ('-v','--version'):
			out = '\tMusic Downloader@Peternguyen - Version : %s'%__version__
			print '-'*(len(out)+15)
			print out
			print '-'*(len(out)+15)
			sys.exit(0)
		elif option in ('-h','--help'):
			help()
			usage()
			sys.exit(0)
		else:
			assert False, "unhandled option"
			sys.exit(0)
	if(link):
		print '-'*(len(link)+4)
		print ' '*20+'List Link Download'    
		for l in link:
			print' ->'+l
		print '-'*(len(link)+4)
		print 'Getting Data ....'
		time.sleep(1)
		for l in link:
			if filter_link_mp3(l) == 'mp3.zing.vn':
				music_site=Mp3Zing(l)
			elif filter_link_mp3(l) == 'www.nhaccuatui.com':
				music_site=NhacCuaTui(l)
			elif filter_link_mp3(l) == 'nhacso.net':
				music_site=NhacSo(l)
			else:
				print 'This %s program support mp3.zing.vn,nhaccuatui.com,nhacso.net' % sys.argv[0]
				sys.exit(0)
			music_site.xml_get_data()
			print 'Downloading......'
			if not extract:
				downloader(music_site.link_song,music_site.name_song,music_site.artist_name,save,music_site.ext,tool)
			else:
				fw = open(extract,'a')
				fw.write(music_site.link_song+'\n')
				fw.close()
	
# MAIN PROGRAM #
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print 'Download Was Interrupted'