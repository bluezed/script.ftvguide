#
# FTV Guide
# Copyright (C) 2015
#      Thomas Geppert [bluezed] - bluezed.apps@gmail.com
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
from operator import itemgetter

ADDON = xbmcaddon.Addon(id='script.ftvguide')


class GuideTypes(object):
    GUIDE_ID = 0
    GUIDE_SORT = 1
    GUIDE_NAME = 2
    GUIDE_FILE = 3
    GUIDE_DEFAULT = 4

    CUSTOM_FILE_ID = 6

    guideTypes = []
    guideParser = ConfigParser.ConfigParser()

    def __init__(self):
        try:
            path = os.path.join(ADDON.getAddonInfo('path'), 'resources', 'guides.ini')
            self.guideParser.read(path)
            guideTypes = []
            defaultGuideId = 0  # fallback to the first guide in case no default is actually set in the ini file
            for section in self.guideParser.sections():
                sectMap = self.SectionMap(section)
                id = int(sectMap['id'])
                file = sectMap['file']
                sortOrder = int(sectMap['sort_order'])
                default = False
                if 'default' in sectMap and sectMap['default'] == 'true':
                    default = True
                    defaultGuideId = id
                guideTypes.append((id, sortOrder, section, file, default))
            self.guideTypes = sorted(guideTypes, key=itemgetter(self.GUIDE_SORT))
            xbmc.log('[script.ftvguide] GuideTypes collected: %s' % str(self.guideTypes), xbmc.LOGDEBUG)

            if str(ADDON.getSetting('xmltv.type')) == '':
                ADDON.setSetting('xmltv.type', str(defaultGuideId))
        except:
            print 'unable to parse guides.ini'

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
