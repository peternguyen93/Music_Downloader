#!/bin/sh
#default python 2
#for Arch Linux | Gentoo
#python2 music_downloader -l "$1" -e /tmp/out.txt
./music_downloader.py -l "$1" -e /tmp/out.txt
vlc --album-art 1 /tmp/out.txt&