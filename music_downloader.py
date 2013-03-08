#!/usr/bin/python
# -*- encoding: utf-8 -*-

__author__ = "Peter Nguyen"
__version__ = "3.0.4 release"

import urllib2,urlparse
import re,time,random
import sys,getopt,os,platform
from xml.etree import ElementTree as ET
from subprocess import call

hdrs = {
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0',
	'Accept-Language':'en-US,en;q=0.5',
	'Cache-Control': 'max-age=0',
	'Accept-Encoding': 'gzip, deflate, sdch',
	'Connection': 'keep-alive'
}

def show_size(size):
	KB = 1024
	MB = KB*1024
	GB = 1024*MB
	output = '%.2f %s'
	if(size < KB):
		output = output % (size,'B')
	elif size >= KB and size < MB:
		output = output % (size/KB,'KB')
	elif size >=MB and size < GB:
		output = output % (size/MB,'MB')
	else:
		output = output % (size/GB,'GB')
	return output

def show_time(time):
	output = ''
	if(int(time) < 60):
		output+='%d s %.4f' % (int(time),time-int(time))
	elif(time >= 60 and time < 3600):
		output+='%d m %d s %.4f' % (int(time)/60,time%60,time-int(time))
	else:
		output+='%d h %d m %d s %.4f' % (int(time)/60-60,time%60,time-int(time))
	return output

def show_process(proc_name,bytes_write,file_len):
	current = 0
	if(current < 100):
		current = (float(bytes_write)/float(file_len))*100
		if(len(proc_name) > 14):
			proc_name = proc_name[:13]+'...'
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

#update multithreading
def basic_download(url,outfile=''):
	if platform.system() == 'Linux':
		path_symboy = '/'
	elif platform.system() == 'Windows':
		path_symboy = '\\'
		
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
	basename = outfile[outfile.rindex(path_symboy)+1:]
	while True:
		show_process(basename,sum_byte,file_len)
		bs = 1024*random.randint(64,256)
		data = n.read(bs)
		sum_byte+=len(data)
		fw.write(data)
		if(not data):
			break
	end = time.time()
	if(sum_byte == file_len):
		print '\n--> Total : %s - Size : %s' % (show_time(end-start),show_size(file_len))
	else:
		print '\n--> [?] Error Download File!'
	fw.close()
	n.close()
	return 1
#youtube.com  
class YouTube:
	def __init__(self,url,quality,vtype):
		self.url = url #url
		self.quality = quality
		self.vtype = vtype
		self.video_link = None
		self.title = []
		self.video_type = {
			'webm':'video/webm',
			'flv':'video/x-flv',
			'mp4':'video/mp4',
			'3gpp':'video/3gpp'
		}

	def GetLink(self):
		video_id = urlparse.parse_qs(urlparse.urlparse(self.url).query)['v'][0]#get video_id
		req = urllib2.Request('http://www.youtube.com/get_video_info?&video_id='+video_id, headers=hdrs)
		d = urllib2.urlopen(req).read()
		try:
			self.title.append(urlparse.parse_qs(urlparse.unquote(d))['title'][0])#get title of video
			parse = urlparse.parse_qs(d.decode('utf-8'))
			streams = parse['url_encoded_fmt_stream_map'][0].split(',') #get list video url
			if self.vtype and self.quality:
				self.video_link = []
				for i in range(len(streams)):
					read_stream = urlparse.parse_qs(streams[i])
					type = read_stream['type'][0].split(';')[0]
					quality = read_stream['quality'][0]
					if type == self.video_type[self.vtype] and quality == self.quality:
						self.video_link.append(read_stream['url'][0]+'&signature='+read_stream['sig'][0])
						break
			if not self.video_link:
				self.video_link = dict()
				for i in range(len(streams)):
					read_stream = urlparse.parse_qs(streams[i])
					type = read_stream['type'][0].split(';')[0]
					type = type.replace('video/','')
					quality = read_stream['quality'][0]
					self.video_link.update({type:quality})
		except KeyError:
			print '[!] Not Find Direct Download Link.'
			exit(1)

class Mp3Zing :
	def __init__ (self,url):
		self.url=url
		self.name_song=[]
		self.artist_name=[]
		self.link_song=[]
		self.ext=[]
		data=urllib2.urlopen(self.url)
		for line in data.read().split('\n'):
			try:
				_rem=re.search(r'xmlURL=(.+?)&',line)
				self.xmllink = _rem.group(1)
			except AttributeError:
				pass
		
	def xml_get_data(self):
		xml=urllib2.urlopen(self.xmllink)
		xml_parse=ET.parse(xml)   
		
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
		root = xml_parse.getroot()
		for item in root:
			self.ext.append('.'+item.attrib['type'])
      
class NhacCuaTui:
	def __init__(self,url):
		self.name_song=[]
		self.artist_name=[]
		self.link_song=[]
		self.ext = []
		
		self.xml_link = 'http://www.nhaccuatui.com/flash/xml?key1='
		
		data = urllib2.urlopen(url).read()
		key1 = re.findall(r'NCTNowPlaying\.intFlashPlayer\(\"flashPlayer\", \"song\", \"(.+?)\"',data)
		self.xml_link += key1[0]
	  
	def xml_get_data(self):
		self.result = urllib2.urlopen(self.xml_link).read()
		self.name_song = re.findall(r'<title>\n        <!\[CDATA\[(.+?)\]\]>',self.result)
		self.link_song = re.findall(r'<location>\n        <!\[CDATA\[(.+?)\]\]>',self.result)
		self.artist_name = re.findall(r'<creator>\n        <!\[CDATA\[(.+?)\]\]>',self.result)
		  
		for item in self.link_song:
			ext = item[item.rfind('.'):len(item)]
			self.ext.append(ext)

class NhacSo:
	def __init__(self,url):
		self.name_song=[]
		self.artist_name=[]
		self.link_song=[]
		self.ext = []
		
		data = urllib2.urlopen(url)
		
		_re = re.findall(r'xmlPath=(.+?)&',data.read())
		if _re:
			self.xml = _re[0]
		
	def xml_get_data(self):
		data = urllib2.urlopen(self.xml)
		
		response = data.read()
		
		self.name_song = re.findall(r'\<name\>\<!\[CDATA\[(.+?)\]\]\>\<\/name\>',response)
		self.artist_name = re.findall(r'\<artist\>\<!\[CDATA\[(.+?)\]\]\>\<\/artist\>',response)
		self.link_song = re.findall(r'\<mp3link\>\<!\[CDATA\[(.+?)\]\]\>\<\/mp3link\>',response)
	    
		for item in self.link_song:
			ext = item[item.rfind('.'):len(item)]
			self.ext.append(ext)

def filter_link_mp3(link):
	return urlparse.urlparse(link)[1]  
  
def downloader(link_song,name_song,artist_name,path,ext,tool_download=None):
	mp3file_list = []
	if not os.path.isdir(path):
		os.mkdir(path)
	if type(artist_name) == list:
		flag = True
	else:
		flag = False
	for item in range(len(link_song)):
		if flag:
			name_song[item] = name_song[item].strip(' \t\n\r')+' - '+artist_name[item]+ext[item]
		else:
			name_song[item] = name_song[item].strip(' \t\n\r')+ext[item]
		mp3file_list.append(path+name_song[item])
	
	if(tool_download == 'wget'):
		flag='-O'
	elif(tool_download == 'axel' or tool_download == 'curl'):
		flag='-o'
		
	for item in range(len(link_song)):
		print '-> Saving to : ' + mp3file_list[item]
		if (tool_download):
			download=[tool_download]
			download.append(link_song[item])
			download.append(flag)
			download.append(mp3file_list[item])
			call(download)
		else:
			basic_download(link_song[item],mp3file_list[item])

def usage():
	print 'Usage ./%s -s <path> -l <link> (-t wget option)' % sys.argv[0]

def help():
	print '''
	-t|--tool : axel,wget,curl
	-l|--link : url link list
	-s|--save : path
	-e|--extract : path or show to show link
	-q|--quality : use only for youtube
	-v|--version : version
	-h|--help : help
	
	* If using option -e, this tool doesn't download files, instead, extracting link file to file text'
	'''
def main():
	support_tools = ['wget','axel','curl']
	tool = None
	link = []
	save = os.getcwd()
	extract = ''
	quality = None #use for youtube
	try:
		opts,args = getopt.getopt(sys.argv[1:],'t:l:s:e:q:vh',['tool','link','save','quality','extract','version','help'])
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
			save = variable
		elif option in ('-e','--extract'):
			extract = variable
		elif option in ('-q','--quality'):
			quality = variable
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
	if platform.system() == 'Windows' and tool:
		print 'This tools not support in Windows'
		for tool in support_tools:
			print '[+] %s' % tool
		sys.exit(0)
	if platform.system() == 'Linux':
		save = os.path.expanduser(save)
		extract = os.path.expanduser(extract)
	if(link):
		print '-'*(len(link[0])+4)
		print ' '*20+'List Link Download'    
		for l in link:
			print' ->'+l
		print '-'*(len(link[0])+4)
		print 'Getting Data ....'
		for l in link:
			music_site = video = None
			if filter_link_mp3(l) == 'mp3.zing.vn':
				music_site = Mp3Zing(l)
			elif filter_link_mp3(l) == 'www.nhaccuatui.com':
				music_site = NhacCuaTui(l)
			elif filter_link_mp3(l) == 'nhacso.net':
				music_site = NhacSo(l)
			elif filter_link_mp3(l) == 'www.youtube.com':
				if quality and ':' in quality:
					extension = quality.split(':')[0]
					q = quality.split(':')[1]
				else:
					extension = None
					q = None
				video = YouTube(l,q,extension)
			else:
				print 'This program support mp3.zing.vn,nhaccuatui.com,nhacso.net,youtube.com'
				sys.exit(0)

			if music_site:
				music_site.xml_get_data()
				link_song = music_site.link_song
				name_song = music_site.name_song
				artist_name = music_site.artist_name
				ext = music_site.ext
				flag = True
			if video:
				video.GetLink()
				link_song = video.video_link
				name_song = video.title
				artist_name = None
				if video.vtype:
					ext = ['.'+video.vtype]
				else:
					ext = None
				flag = False

			if not extract:
				print 'Downloading %s......' % l
				if not flag:
					if type(link_song) == dict:
						print 'This video %s contains : ' % l 
						for k in video.video_link:
							print '\t[+] '+k+':'+video.video_link[k]
						print 'Try : %s -l %s -q type:quality -s <path>' % (sys.argv[0],l)
						exit(0)
				downloader(link_song,name_song,artist_name,save,ext,tool)
			else:
				print 'Extracting %s.......' % l
				if (extract == 'show'):
					print '-'*53
					for item in link_song:
						print '[+] ',item
				else:
					fw = open(extract,'a')
					for item in link_song:
						fw.write(item+'\n')
					fw.close()
	
# MAIN PROGRAM #
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print 'Download Was Interrupted'