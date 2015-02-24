#
#      FTV Guide
#      Copyright (C) 2015
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
import xbmcgui
import xbmcaddon

from strings import *

ADDON = xbmcaddon.Addon(id = 'script.ftvguide')

guideTypes = [(30126, 'guide.xmltv'), (30127, 'guide_basic.xmltv'), (30133, 'guide_ukbasic.xmltv'), 
              (30134, 'guide_uksky.xmltv'), (30135, 'guide_ustvnow.xmltv'), (30136, 'guide_usukbasic.xmltv'), 
              (30142, 'CUSTOM')]

def getGuideFileName(id):
    return guideTypes[id][1]

if __name__ == '__main__':
    list = []
    for id, file in guideTypes:
        list.append(strings(id))
    d = xbmcgui.Dialog()
    ret = d.select('Select what type of guide you want to use', list)
    ADDON.setSetting('xmltv.type', str(ret))
    ADDON.setSetting('xmltv.type_select', strings(guideTypes[ret][0]))
