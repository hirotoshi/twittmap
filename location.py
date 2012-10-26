# coding=utf-8
#!/usr/bin/env python


import yaml
import logging
from google.appengine.api import urlfetch
from django.utils import simplejson
import os
import urllib
import urllib2
import base64

class LocationFinder:
  config = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r'))
  google_key = config['google_key']
  yjdn_appid = config['yjdn_appid']
  geodosu_key = config['geodosu_key']

  def find(self,keyword):
    #Y! LocalSearch
    ret = self.getLocalSearch( keyword )
    if int(ret['Count']) > 0:
      #見つかった
      if 'Title' in ret['Item']:
        loc = ret['Item']
      else:
        loc = ret['Item'][0]

      #Level5はジオドス
      if loc['AddressLevel'] == "5" :
        type = 'geodosu'
      else:
        type = 'yahoo'

      return {
        'title' : loc['Title'],
        'lat'   : loc['DatumWgs84']['Lat'],
        'lon'   : loc['DatumWgs84']['Lon'],
        'level' : loc['AddressLevel'],
        'url'   : u'http://map.yahoo.co.jp/pl?lat=%s&lon=%s'%(loc['DatumTky97']['Lat'],loc['DatumTky97']['Lon'] ) ,
        'type'  : type,
      }

    #Google Search
    ret = self.getGoogleSearch( keyword ) 
    if ret['Status']['code'] == 200 :
      loc = ret['Placemark'][0]
      coord = loc['Point']['coordinates']
      return {
        'title' : loc['address'],
        'lat'   : coord[1],
        'lon'   : coord[0],
        'level' : loc['AddressDetails']['Accuracy'],
        'url'   : 'http://maps.google.com/?' + 
                  urllib.urlencode( { 
                    "ie"  : "utf-8",
                    "q"   : loc['address'].encode("utf-8"),
                    "ll"  : str(coord[1]) + "," + str(coord[0]),
                  }),
        'type'  : 'google',
      }


    return None    

 
  #Google Search
  def getGoogleSearch(self,keyword):
    url = "http://maps.google.com/maps/geo?"
    #url = "http://api.geodosu.com/" + self.geodosu_key + "/maps/google.com/maps/geo?"
    url += urllib.urlencode({
          "key"     : self.google_key,
          "q"       : keyword.encode("utf-8"),
          "output"  : "json",
        })
    result = urlfetch.fetch( url , method=urlfetch.GET)
    return simplejson.loads( result.content)

  #LocalSearchを実行
  def getLocalSearch(self,keyword):
    url = 'http://map.yahooapis.jp/LocalSearchService/V1/LocalSearch?'
    url = 'http://api.geodosu.com/' + self.geodosu_key + '/map.yahooapis.jp/LocalSearchService/V1/LocalSearch?'
    url +=  urllib.urlencode({
              "appid" : self.yjdn_appid ,
              "p"     : keyword.encode("utf-8"),
              "o"     : "json",
              "datum" : "wgs" })
    result = urlfetch.fetch( url , method=urlfetch.GET)
    return simplejson.loads( result.content )


