#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2013- PeterNguyen <https://github.com/peternguyen93>
#
# Music_Downloader is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Music_Downloader.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Peter Nguyen"
__version__ = "3.2.2"

import urllib2,urlparse
import re,time,random
import sys,getopt,os,platform
from xml.etree import ElementTree as ET
from subprocess import call
import zlib
import StringIO

'''Define header http to request data from server'''
hdrs = {
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
	Chrome/29.0.1547.76 Safari/537.36',
	'Accept-Language':'en-US,en;q=0.5',
	'Cache-Control': 'max-age=0',
	'Accept-Encoding': 'gzip, deflate, sdch',
	'Connection': 'keep-alive'
}
#define path_symbol
if platform.system() == 'Linux' or platform.system() == 'Darwin':
	path_symbol = '/'
elif platform.system() == 'Windows':
	path_symbol = '\\'
# BasicDownload Class
class BasicDownload:
	def __init__(self,url,outfile = ''):
		self.url = url
		self.outfile = outfile
	# startDownload
	def startDownload(self):
		''' 
			- Check Path Symboy for each platform
			- Get file length and file type
			- Check file exists
			- Start download file
		'''
		
		try:
			print self.url
			# req = urllib2.Request(self.url, headers=hdrs)
			n = urllib2.urlopen(self.url)
			file_len = int(n.info().getheaders('content-length')[0]) #get file size
			file_type = n.info().getheaders('content-type')[0] #get file type
			file_type = file_type[len(file_type)-3:len(file_type)]
			
			if(os.path.exists(self.outfile) and os.path.getsize(self.outfile) == file_len):
				return 0
			if(not self.outfile):
				self.outfile+=os.getcwd()+'outfile'+'.'+file_type
			fw = open(self.outfile,'wb')
			sum_byte=0
			start = time.time()
			basename = self.outfile[self.outfile.rindex(path_symbol)+1:]
			while 1:
				self.show_process(basename,sum_byte,file_len)
				bs = 1024*random.randint(64,256) #random bytes read
				data = n.read(bs)
				sum_byte+=len(data)
				fw.write(data)
				if(not data):
					break
			end = time.time()
			if(sum_byte == file_len):
				print '\n--> Total : %s - Size : %s' % (self.show_time(end-start),self.show_size(file_len))
			else:
				print '\n--> [?] Error Download File!'
			fw.close()
		except urllib2.HTTPError, err:
			print '[!] HTTP Connect Error, Please Check Connection'
			return 0
		except urllib2.URLError, e:
			print '[!] HTTP Error : ', e.code
			return 0
		# finally:
			# print '[DEBUG] ',self.url
		return 1
	# show ProcessBar
	def show_process(self,proc_name,bytes_write,file_len):
		'''Show process of file download'''
		current = 0
		if(current < 100):#check if current less than 100 percent
			current = (float(bytes_write)/float(file_len))*100#calculate percent
			if(len(proc_name) > 14):#if length of name rather than 14 character get 13 character
				proc_name = proc_name[:13]+'...'
			output='\r --> %s [' % proc_name
			for i in range(1,int(current/2)+1):#print '#' fill processBar
				output+='#'
			for i in range(1,int((100-current)/2)+1):#print ' ' to present part not download
				output+=' '
			if(current < 100):#print percent 
				end_str = '] '+'{0:.2f}'.format(current)+'%'
			else:#end processBar
				end_str = '] 100%|Done'
			output+=end_str
			sys.stdout.write(output.encode('utf-8'))
		sys.stdout.flush()
	
	def show_size(self,size):
		'''Show size of file'''
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

	def show_time(self,time):
		'''Calculate time and display'''
		output = ''
		if(int(time) < 60):
			output+='%d s %.4f' % (int(time),time-int(time))
		elif(time >= 60 and time < 3600):
			output+='%d m %d s %.4f' % (int(time)/60,time%60,time-int(time))
		else:
			output+='%d h %d m %d s %.4f' % (int(time)/60-60,time%60,time-int(time))
		return output
'''
	- This Class Setup Method to parse Youtube Url and get Direct Video URL
'''
class YouTube:
	def __init__(self,url,quality,vtype):
		self.url = url #url
		self.quality = quality #quality
		self.vtype = vtype #video type
		self.video_link = None
		self.title = []
		# define video file type of youtube support
		self.video_type = {
			'webm':'video/webm',
			'flv':'video/x-flv',
			'mp4':'video/mp4',
			'3gpp':'video/3gpp'
		}

	def GetLink(self):
		'''
			- Parse param v and get video id
			- Use http://www.youtube.com/get_video_info?&video_id= to get link and quality
			- Direct Link : url_encoded_fmt_stream_map + &signature= +sig
		'''
		try:
			video_id = urlparse.parse_qs(urlparse.urlparse(self.url).query)['v'][0]#get video_id
		except KeyError:
			print '[?] Link Error'
			sys.exit(1)
		req = urllib2.Request('http://www.youtube.com/get_video_info?&video_id='+video_id, headers=hdrs)
		d = urllib2.urlopen(req).read()
		try:
			file_title = urlparse.parse_qs(urlparse.unquote(d))['title'][0]#get title of video
			parse = urlparse.parse_qs(d.decode('utf-8'))
			streams = parse['url_encoded_fmt_stream_map'][0].split(',') #get list video url
			if self.vtype and self.quality:
				self.video_link = []
				for i in range(len(streams)):
					read_stream = urlparse.parse_qs(streams[i])
					file_type = read_stream['type'][0].split(';')[0]
					quality = read_stream['quality'][0]
					if file_type == self.video_type[self.vtype] and quality == self.quality:
						self.video_link.append(read_stream['url'][0])
						self.title.append(file_title+'.'+self.vtype)
						break
			if not self.video_link:
				self.video_link = []
				for i in range(len(streams)):
					read_stream = urlparse.parse_qs(streams[i])
					file_type = read_stream['type'][0].split(';')[0]
					file_type = file_type.replace('video/','')
					quality = read_stream['quality'][0]
					self.video_link.append((file_type,quality))
		except KeyError:
			print '[!] Not Find Direct Download Link.'
			exit(1)

'''
	Class Mp3Zing,NhacCuaTui,NhacSo Provide same Method Parse URL, get XML link and parse it to get
	direct mediafile for download
'''
class Mp3Zing :
	def __init__ (self,url):
		self.list_files = []
		self.link_song = []
		data = urllib2.urlopen(url).read()
		#decompress data recv from server
		data = zlib.decompress(data,16+zlib.MAX_WBITS)
		matches = re.findall(r'xmlURL=(.+?)&',data)
		try:
			self.xmllink = matches[0]
		except IndexError:
			print '[?] Not Find Direct Link'
			sys.exit(1)
			
	def xml_get_data(self):
		'''
			- Parse xmlURl
			- Read xmlFile and parse sytax
			- Get Data From xmlFile
		'''
		try:
			xml = urllib2.urlopen(self.xmllink)
			decompress = zlib.decompress(xml.read(),16+zlib.MAX_WBITS)
			#decompress string object as file object
			xml = StringIO.StringIO(decompress)
			xml_parse = ET.parse(xml)
			name_song = []
			for name in xml_parse.findall('.//title'):
				name_song.append(unicode(name.text))
			artist_name = []
			for artist in xml_parse.findall('.//performer'):
				artist_name.append(unicode(artist.text))
			if(not xml_parse.findall('.//f480')):
				for link in xml_parse.findall('.//source'):
					self.link_song.append(unicode(link.text))
			else:
				for link in xml_parse.findall('.//f480'):
					self.link_song.append(unicode(link.text))
			# get file type
			root = xml_parse.getroot()
			ext = []
			for child in root:
				attrib = child.get('type') # find attribute of element item
				if attrib:
					ext.append('.'+child.attrib['type'])
				
			for i in xrange(len(self.link_song)):
				name_song[i] = name_song[i].strip(' \r\t\n')
				artist_name[i] = artist_name[i].strip(' \r\t\n')
				fullname = name_song[i] + ' - ' + artist_name[i] + ext[i]
				self.list_files.append(fullname.strip(' \r\t\n'))
		except urllib2.HTTPError:
			print '[!] HTTP Connect Error, Please Check Connection'
			sys.exit(1)
		except urllib2.URLError, e:
			print '[!] HTTP Error : ', e.code
			sys.exit(1)
      
class NhacCuaTui:
	def __init__(self,url):
		self.list_files = []
		self.link_song = []
		self.xml_link = ''
		self.url = url

		if 'video' not in url:
			# get music links from url
			self.xml_link = 'http://www.nhaccuatui.com/flash/xml'
			data = urllib2.urlopen(url).read()
			key = re.findall(r'NCTNowPlaying\.intFlashPlayer\(\"flashPlayer\", \"(song|playlist)\", \"(.+?)\"',data)
			try:
				if key[0][0] == 'playlist':
					self.xml_link += '?key2='+key[0][1] #get playlist
				elif key[0][0] == 'song':
					self.xml_link += '?key1='+key[0][1] #get song
				else:
					print '[?] Not Match Key'
			except IndexError:
				print '[?] Not Found Direct Link'
				sys.exit(1)
		# get videos from url
		# re.findall(r'\<meta itemprop=\"contentURL\" content=\"(.+?)\" \/\>',d)

	def xml_get_data(self):
		'''
			- Parse key1 value from webpage
			- Read xmlFile and parse sytax
			- Get Data From xmlFile
		'''
		if self.xml_link:
			try:
				name_song = []
				artist_name = []
				result = urllib2.urlopen(self.xml_link)
				xml = ET.parse(result) #parse xml
				
				for node in xml.findall('track'): #find all node track
					self.link_song.append(node.find('location').text)
					name_song.append(node.find('title').text)
					artist_name.append(node.find('creator').text)
				
				for i in xrange(len(self.link_song)):
					name_song[i] = name_song[i].strip(' \r\t\n')
					artist_name[i] = artist_name[i].strip(' \r\t\n')
					ext = self.link_song[i][self.link_song[i].rfind('.'):len(self.link_song[i])]
					fullname = name_song[i] + ' - ' + artist_name[i] + ext
					self.list_files.append(fullname.strip(' \r\t\n'))
			except urllib2.HTTPError:
				print '[!] HTTP Connect Error, Please Check Connection'
				sys.exit(1)
			except urllib2.URLError, e:
				print '[!] HTTP Error : ', e.code
				sys.exit(1)
		else:
			# getting video from nhaccuatui.com
			d = urllib2.urlopen(self.url).read()
			self.link_song = re.findall(r'\<meta itemprop=\"contentURL\" content=\"(.+?)\" \/\>',d)
			# video link has only one link
			self.list_files.append(os.path.basename(self.link_song[0]))

class NhacSo:
	def __init__(self,url):
		self.list_files = []
		self.link_song = []
		
		data = urllib2.urlopen(url)
		_re = re.findall(r'xmlPath=(.+?)&',data.read())
		try:
			self.xml = _re[0]
		except IndexError:
			print '[?] Not Found Direct Link'
			sys.exit(1)
		
	def xml_get_data(self):
		'''
			- Parse xmlPath
			- Read xmlFile and parse sytax
			- Get Data From xmlFile
		'''
		try:
			xml = urllib2.urlopen(self.xml)
			response = xml.read()
			name_song = re.findall(r'\<song\>\n \<id\>\d+\<\/id\>\n\n\<totalTime\>\d+\<\/totalTime\>\n\n\<name\>\<\!\[CDATA\[(.+?)\]\]\>\<\/name\>',response)
			artist_name = re.findall(r'\<artist\>\<!\[CDATA\[(.+?)\]\]\>\<\/artist\>',response)
			self.link_song = re.findall(r'\<mp3link\>\<!\[CDATA\[(.+?)\]\]\>\<\/mp3link\>',response)
			for i in xrange(len(self.link_song)):
				# print name_song[i]
				name_song[i] = name_song[i].strip(' \r\t\n')
				artist_name[i] = artist_name[i].strip(' \r\t\n')
				ext = self.link_song[i][self.link_song[i].rfind('.'):len(self.link_song[i])]
				fullname = name_song[i] + ' - ' + artist_name[i] + ext
				self.list_files.append(fullname.strip(' \r\t\n'))
		except urllib2.HTTPError:
			print '[!] HTTP Connect Error, Please Check Connection'
			sys.exit(1)
		except urllib2.URLError, e:
			print '[!] HTTP Error : ', e.code
			sys.exit(1)

# http://tv.zing.vn module
class ZingTV:
	def __init__(self,url):
		self.list_files = []
		self.link_song = []

		web_page = urllib2.urlopen(url).read()
		# get xml file
		self.xml_link = re.findall(r'xmlURL: \"(.*)\"',web_page)[0]
		# get html5 link
		self.html5_link = re.findall(r'\<source src=\"(.*)\" type="video/mp4',web_page)[0]

	def xml_get_data(self):
		if self.html5_link and self.xml_link:
			original_link = urllib2.urlopen(self.html5_link).geturl()
			# default get f480 video
			self.link_song.append(original_link.replace('f360','f480'))
			xml = urllib2.urlopen(self.xml_link)
			decompress = zlib.decompress(xml.read(),16+zlib.MAX_WBITS)
			#decompress string object as file object
			xml = StringIO.StringIO(decompress)
			xml_parse = ET.parse(xml)
			fn = [obj.text for obj in xml_parse.findall('.//title')][0]
			fn += ' - ' + [obj.text for obj in xml_parse.findall('.//performer')][0]
			self.list_files.append(fn)
		else:
			print '[!] Error while parsing link'
			sys.exit
  
def downloader(link_song,list_files,path,tool_download=None):
	if not os.path.isdir(path):
		os.mkdir(path) #create folder if it's not exists
	
	if(tool_download == 'wget'):
		flag='-O'
	elif(tool_download == 'axel' or tool_download == 'curl'):
		flag='-o'
	#add path to file_lists
	if path[len(path)-1] != path_symbol:
		path += path_symbol
	for item in xrange(len(list_files)):
		list_files[item] = path + list_files[item]

	for item in range(len(link_song)):
		print '-> Saving to : ' + list_files[item].encode('utf-8')
		if (tool_download):
			download = [tool_download]
			download.append(link_song[item])
			download.append(flag)
			download.append(list_files[item])
			call(download) #call subprocess
		else:
			# call basic_download
			downloader = BasicDownload(link_song[item],list_files[item])
			downloader.startDownload()

def usage():
	'''Usage Function'''
	print 'Usage %s -s <path> -l <link> (-t wget option)' % sys.argv[0]

def help():
	'''Help Function'''
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
	'''
		- Main Function
		- Setup Program
	'''
	support_tools = ['wget','axel','curl'] #support tools download
	tool = None
	link = []
	save = os.getcwd()
	extract = ''
	quality = None #use for youtube
	try:
		opts,args = getopt.getopt(sys.argv[1:],'t:l:s:e:q:vh',
			['tool','link','save','quality','extract','version','help'])
	except getopt.GetoptError as err:
		usage()
		print str(err)
		sys.exit(1)
	for option,variable in opts:
		if option in ('-t','--tool'):
			if(variable in support_tools):
				tool = variable
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
		# if platform is Windows and option tool is set not support other tools
		print 'This tools not support in Windows'
		for tool in support_tools:
			print '[+] %s' % tool
		sys.exit(0)
	
	if platform.system() == 'Linux':
		save = os.path.expanduser(save)
		extract = os.path.expanduser(extract)
	
	if(link):
		#if link is validate
		print '-'*(len(link[0])+4)
		print ' '*20+'List Link Download'    
		for l in link:
			print' ->'+l
		print '-'*(len(link[0])+4)
		print 'Getting Data ....'
		for l in link:
			#check input url or url list
			music_site = video = None
			try:
				host = urlparse.urlparse(l)[1] #Parse Host
			except IndexError:
				print '[!] Wrong Url.'
				sys.exit(0)
			#check host in support download list
			if host == 'mp3.zing.vn':
				music_site = Mp3Zing(l)
			elif host == 'www.nhaccuatui.com':
				music_site = NhacCuaTui(l)
			elif host == 'nhacso.net':
				music_site = NhacSo(l)
			elif host == 'www.youtube.com':
				if quality and ':' in quality:
					extension = quality.split(':')[0]
					q = quality.split(':')[1]
				else:
					extension = None
					q = None
				video = YouTube(l,q,extension)
			elif host == 'tv.zing.vn':
				music_site = ZingTV(l)
			else:
				print 'This program support mp3.zing.vn,nhaccuatui.com,nhacso.net,youtube.com,tv.zing.vn'
				sys.exit(0)
			#if url is in music_site list
			if music_site:
				music_site.xml_get_data()
				link_song = music_site.link_song
				list_files = music_site.list_files
				flag = True
			#if url is youtube
			if video:
				video.GetLink()
				link_song = video.video_link
				list_files = video.title
				artist_name = None
				if video.vtype:
					ext = ['.'+video.vtype]
				else:
					ext = None
				flag = False
			#if not use option -e| --extract
			if not extract:
				print 'Downloading %s......' % l
				if not flag:#check if host is Youtube and not set option quality
					if not quality:
						print 'Videos quality:'
						for link in link_song:
							print '\t[+] '+link[0]+':'+link[1]
						print 'Try : %s -l %s -q type:quality -s <path>' % (sys.argv[0],l)
						exit(0)
				if(link_song): #if link is get, download link and save to file
					downloader(link_song,list_files,save,tool)
				else:
					print '[!] Direct Url Not Found.'
					sys.exit(1)
			else:
				#if -e option turn on, extract link to text file
				print 'Extracting %s.......' % l
				if (extract == 'show'): #view link
					print '-'*53
					for item in link_song:
						print '[+] ',item
				else:
					fw = open(extract,'a')
					for item in link_song:
						fw.write(item+'\n')
					fw.close()
	else:
		usage()
	
# MAIN PROGRAM #
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print '[!] Download Was Interrupted'