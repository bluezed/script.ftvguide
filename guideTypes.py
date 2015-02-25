#
# FTV Guide
# Copyright (C) 2015
# Thomas Geppert [bluezed] - bluezed.apps@gmail.com
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
import xbmc
import xbmcgui
import xbmcaddon

import os
import ConfigParser
import urllib2
import datetime
import zlib

from operator import itemgetter
from strings import *

ADDON = xbmcaddon.Addon(id='script.ftvguide')


class GuideTypes(object):
    GUIDE_ID = 0
    GUIDE_SORT = 1
    GUIDE_NAME = 2
    GUIDE_FILE = 3
    GUIDE_DEFAULT = 4

    CUSTOM_FILE_ID = 6

    INTERVAL_ALWAYS = 0
    INTERVAL_12 = 1
    INTERVAL_24 = 2
    INTERVAL_48 = 3

    guideTypes = []
    guideParser = ConfigParser.ConfigParser()
    filePath = xbmc.translatePath(os.path.join('special://profile', 'addon_data', 'script.ftvguide', 'guides.ini'))
    URL = MAIN_URL + 'guides.ini'

    def __init__(self):
        try:
            self.fetchFile()

            self.guideParser.read(self.filePath)
            guideTypes = []
            defaultGuideId = 0  # fallback to the first guide in case no default is actually set in the ini file
            for section in self.guideParser.sections():
                sectMap = self.SectionMap(section)
                id = int(sectMap['id'])
                fName = sectMap['file']
                sortOrder = int(sectMap['sort_order'])
                default = False
                if 'default' in sectMap and sectMap['default'] == 'true':
                    default = True
                    defaultGuideId = id
                guideTypes.append((id, sortOrder, section, fName, default))
            self.guideTypes = sorted(guideTypes, key=itemgetter(self.GUIDE_SORT))
            xbmc.log('[script.ftvguide] GuideTypes collected: %s' % str(self.guideTypes), xbmc.LOGDEBUG)

            if str(ADDON.getSetting('xmltv.type')) == '':
                ADDON.setSetting('xmltv.type', str(defaultGuideId))
        except:
            print 'unable to parse guides.ini'

    def fetchFile(self):
        fetch = False
        if not os.path.exists(self.filePath):  # always fetch if file doesn't exist!
            fetch = True
        else:
            interval = int(ADDON.getSetting('xmltv.interval'))
            if interval <> self.INTERVAL_ALWAYS:
                modTime = datetime.datetime.fromtimestamp(os.path.getmtime(self.filePath))
                td = datetime.datetime.now() - modTime
                # need to do it this way cause Android doesn't support .total_seconds() :(
                diff = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6) / 10 ** 6
                if ((interval == self.INTERVAL_12 and diff >= 43200) or
                        (interval == self.INTERVAL_24 and diff >= 86400) or
                        (interval == self.INTERVAL_48 and diff >= 172800)):
                    fetch = True
            else:
                fetch = True

        if fetch:
            tmpFile = xbmc.translatePath(os.path.join('special://profile', 'addon_data', 'script.ftvguide', 'tmp'))
            f = open(tmpFile, 'wb')
            tmpData = urllib2.urlopen(self.URL)
            data = tmpData.read()
            if tmpData.info().get('content-encoding') == 'gzip':
                data = zlib.decompress(data, zlib.MAX_WBITS + 16)
            f.write(data)
            f.close()
            if os.path.getsize(tmpFile) > 256:
                if os.path.exists(self.filePath):
                    os.remove(self.filePath)
                os.rename(tmpFile, self.filePath)
                xbmc.log('[script.ftvguide] guides.ini downloaded', xbmc.LOGDEBUG)

    def SectionMap(self, section):
        dict1 = {}
        options = self.guideParser.options(section)
        for option in options:
            try:
                dict1[option] = self.guideParser.get(section, option)
                if dict1[option] == -1:
                    xbmc.log('[script.ftvguide] skip: %s' % option, xbmc.LOGDEBUG)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1


    def getGuideDataItem(self, id, item):
        value = None
        guide = self.getGuideById(id)
        try:
            value = guide[item]
        except IndexError:
            xbmc.log('[script.ftvguide] DataItem with index %s not found' % item, xbmc.LOGDEBUG)
        return value


    def getGuideById(self, id):
        xbmc.log('[script.ftvguide] Finding Guide with ID: %s' % id, xbmc.LOGDEBUG)
        ret = []
        for guide in self.guideTypes:
            if guide[self.GUIDE_ID] == int(id):
                ret = guide
                xbmc.log('[script.ftvguide] Found Guide with data: %s' % str(guide), xbmc.LOGDEBUG)
        return ret


if __name__ == '__main__':
    list = []
    gTypes = GuideTypes()
    for type in gTypes.guideTypes:
        list.append(type[gTypes.GUIDE_NAME])
    d = xbmcgui.Dialog()
    ret = d.select('Select what type of guide you want to use', list)
    if ret >= 0:
        guideId = gTypes.guideTypes[ret][gTypes.GUIDE_ID]
        ADDON.setSetting('xmltv.type', str(guideId))
        ADDON.setSetting('xmltv.type_select', gTypes.getGuideDataItem(guideId, gTypes.GUIDE_NAME))
