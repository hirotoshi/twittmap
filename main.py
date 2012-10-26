# coding=utf-8
#!/usr/bin/env python


import wsgiref.handlers

import os
import yaml
import re
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from django.utils import simplejson
from google.appengine.api import urlfetch
from status import Status
from twitter import TwitterClient
import urllib,urllib2
from location import LocationFinder



#Webページ
class MainHandler(webapp.RequestHandler):
  config = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r'))
  username = config['twitter_username']
  yjdn_appid = config['yjdn_appid']
  google_key = config['google_key']
 
  def get(self):
    twitter = TwitterClient()
    statuses = Status.getStatuses(20)
    user = twitter.getUser( self.username )

    def urlify(txt):
      if txt:
        txt = re.sub('(https?:\/\/[-_.!~*\'()a-zA-Z0-9;/?:@&=+$,%#]+)',  
                 '<a href="\\1">Link</a>', txt)
      return txt

    def getMapUrl(loc,type):
      if not loc:
        return None;

      if type == "google" :
        url = u'http://maps.google.com/staticmap?'
        url += urllib.urlencode( {
          'center'  : str(loc.lat) + ',' + str(loc.lon),
          'markers' : str(loc.lat) + ',' + str(loc.lon),
          'size'    : '460x320',
          'zoom'    : '15',
          'key'     : self.google_key,
        } )
      else :
        url = u'http://tp.map.yahoo.co.jp/mk_map?'
        url += urllib.urlencode( {
          'prop'      : 'clip_map',
          'scalebar'  : 'off',
          'pointer'   : 'off',
          'width'     : '460',
          'height'    : '320',
          'datum'     : 'wgs84',
          'lat'       : loc.lat,
          'lon'       : loc.lon,
          'pin'      : str(loc.lat) + "," + str(loc.lon),
          'sc'        : 4,
        })

      return url
  
    list = []
    for status in statuses:
      list.append( {
          'text'  : status.text,
          'reply' : urlify(status.reply),
          'user_screen_name' : status.user_screen_name,
          'user_profile_image_url' : status.user_profile_image_url,
          'loc_url' : status.loc_url,
          'map'   : getMapUrl( status.loc_point , status.loc_type ),
      })

    values = {
               'list'   : list,
               'user'   : user,
                }
    path = os.path.join(os.path.dirname(__file__), 'main.html')
    self.response.out.write( template.render(path,values))


#テスト用ページ
class TestHandler(webapp.RequestHandler):
  @login_required
  def get(self):
    keyword = u'京都市中京区御池通間之町東入ル'
    finder = LocationFinder()
    loc = finder.find( keyword )
    self.response.out.write( '<pre>' + simplejson.dumps(loc,indent=4,ensure_ascii=False) + '</pre>' )

    keyword = u'東京'
    finder = LocationFinder()
    loc = finder.find( keyword )
    self.response.out.write( '<pre>' + simplejson.dumps(loc,indent=4,ensure_ascii=False) + '</pre>' )

    keyword = u'六本木a'
    finder = LocationFinder()
    loc = finder.find( keyword )
    self.response.out.write( '<pre>' + simplejson.dumps(loc,indent=4,ensure_ascii=False) + '</pre>' )




def main():
  application = webapp.WSGIApplication([('/', MainHandler),
                                        ('/test', TestHandler),
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
