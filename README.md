Music_Downloader
================

Music Downloader

Author: peternguyen
Version: 3.0.5 release
License: GNU General Public License <http://www.gnu.org/licenses/>

Site Music Support:
- mp3.zing
- nhaccuatui
- nhacso.net
- youtube.com

Function:
- Support download more than 1 files
- Support extract url to file text using option -e
- Addon Support Playing Musics or Videos With VLC
- Support download video on youtube.com
- Recommend use axel or curl to download video from youtube.com
- Work on Windows, not support wget,curl,axel on windows, you can't only use basic downloader

Example:
- ex:
	- ./music_downloader.py -s ~/Musics/Xuan/ -l "http://www.nhaccuatui.com/nghe?M=_CCBim8jAW http://www.nhaccuatui.com/nghe?M=mxuilr6eny"
- ex for youtube:
	- ./music_downloader.py -s ~/ -l https://www.youtube.com/watch?v=oPW6xo_fq94 -q type:quality
	- if you don't know type or quality, you will remove option -q and program shows you list of type:quality, which support by video link
	- ./music_downloader.py -s ~/ -l https://www.youtube.com/watch?v=oPW6xo_fq94 -q mp3:medium
