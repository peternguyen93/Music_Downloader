#!/usr/bin/python
# -*- encoding: utf-8 -*-

__author__ = "Peter Nguyen"
__version__ = "3.0 beta"

import urllib
import urllib2
import re
import httplib
import sys
import os
import time
import getopt
import random
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
			end_str = '] '+str(current)+'%'
			output+=end_str
		else:
			end = '] 100%|Done'
			output+=end
		sys.stdout.write(output)
	sys.stdout.flush()

def basic_download(url,outfile=''):
	req = urllib2.Request(url, headers=hdrs)
	n = urllib2.urlopen(req)
	file_len = int(n.info().getheaders('content-length')[0])
	file_type = n.info().getheaders('content-type')[0]
	
	if(os.path.exists(outfile) and os.path.getsize(outfile) == file_len):
		return 0
	if(not outfile):
		outfile+=os.getcwd()+'outfile'+'.'+file_type
	fw = open(outfile,'wb')
	sum_byte=0
	start = time.time()
	while True:
		show_process(outfile,sum_byte,file_len)
		bs = 1024*random.randint(10,100)
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
			except AttributeError:
				pass
	def xml_get_data(self):
		xml=urllib.urlopen(self.xmllink)
		xml_parse=ElementTree.parse(xml)   
		
		for name in xml_parse.findall('.//title'):
			self.name_song.append(unicode(name.text))
		for artist in xml_parse.findall('.//performer'):
			self.artist_name.append(unicode(artist.text))
		for link in xml_parse.findall('.//source'):
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
	if not os.path.isdir(path):
		os.mkdir(path)
	
	if(tool_download):
		if(tool_download == 'wget'):
			flag='-O'
		elif(tool_download == 'axel'):
			flag='-o'
		    
		for item in range(len(name_song)):      
			download=[tool_download]
			name_song[item]+=' - '+artist_name[item]+ext[item]
			mp3_file_location=path+'/'+name_song[item]
			download.append(link_song[item])
			download.append(flag)
			download.append(mp3_file_location)
			call(download)
	else:
		for item in range(len(name_song)):
			name_song[item]+=' - '+artist_name[item]+ext[item]
			mp3_file_location=path+'/'+name_song[item]
			basic_download(link_song[item],mp3_file_location)   

def usage():
	print 'Usage ./%s -s <path> -l <link> (-t wget option)'

def help():
	print '''
	-t|--tool : axel,wget,download tools,.....
	-l|--link : url link list
	-s|--save : path
	-v|--version : version
	-h|--help : help
	'''
def main():
	support_tools = ['wget','axel']
	tool = None
	link = []
	save = os.getcwd()
	try:
		opts,args = getopt.getopt(sys.argv[1:],'t:l:s:vh',['tool','link','save','version','help'])
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
			downloader(music_site.link_song,music_site.name_song,music_site.artist_name,save,music_site.ext,tool)
	
# MAIN PROGRAM #
if __name__ == '__main__':
	main()