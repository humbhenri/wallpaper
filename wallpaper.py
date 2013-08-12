#!/usr/bin/python
# Download one of the top wallpapers at http://www.reddit.com/r/EarthPorn/top/ and set it like desktop background
# Copyright (C) 2013 Humberto Pinheiro

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

from BeautifulSoup import BeautifulSoup
import os
import platform
import subprocess
import time
import urllib2


URL = 'http://www.reddit.com/r/EarthPorn/top/'
IMGS_EXT = ('jpg', 'png', 'jpeg', 'JPG', 'PNG', 'JPEG')
wallpaper = None
MAC_SCRIPT = """/usr/bin/osascript<<END
tell application "Finder"
set desktop picture to {"%s"} as alias
end tell
END"""


def convert_to_hfs(path):
    hfs_path = subprocess.check_output(
        ['/usr/bin/osascript', '-e', 'return posix file "%s"' % path])
    return hfs_path.replace('file', '').strip()


def convert_to_bmp(path_to_image):
    from PIL import Image
    bmp_image = Image.open(path_to_image)
    filename = os.path.basename(path_to_image)
    filename = os.path.splitext(filename)[0] + ".BMP"
    bmp_image.save(filename, "BMP")
    return os.path.join(os.getcwd(), filename).encode('utf-8')


def set_wallpaper(path_to_image):
    system = platform.system()
    if system == 'Darwin':
        subprocess.Popen(MAC_SCRIPT %
                         convert_to_hfs(path_to_image), shell=True)
        time.sleep(10)  # launchd requires that the job runs for at least 10s
    elif system == 'Windows':
        from ctypes import windll
        bmp = convert_to_bmp(path_to_image)
        windll.user32.SystemParametersInfoA(20, 0, bmp, 0)
        os.remove(path_to_image)
        os.remove(bmp)


# parse the page, looking for the link of the top most wallpaper
soup = BeautifulSoup(urllib2.urlopen(URL))
for a in soup.findAll('a', {'class': 'title '}):
    if a.get('href').endswith(IMGS_EXT):
        wallpaper = a.get('href')
        break

# set the desktop background
if wallpaper is not None:
    img = urllib2.urlopen(wallpaper).read()
    filename = os.path.basename(wallpaper)
    output = open(filename, 'wb')
    output.write(img)
    output.close()
    set_wallpaper(os.path.realpath(filename))
