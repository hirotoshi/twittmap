# coding=utf-8
#!/usr/bin/env python


import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from django.utils import simplejson
import os
import urllib
import urllib2
import base64
import yaml
import logging
from status import Status
from twitter import TwitterClient
from location import LocationFinder

   

#cronから呼び出されるページの処理
class CronHandler(webapp.RequestHandler):

  config = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r'))
  username = config['twitter_username']
  fail_message = config['fail_message']
  success_message = config['success_message']

  #メインの処理
  def get(self):

    debug = self.request.get('debug',False)
    self.response.out.write('<ul>')

    #自分宛のreplyを取得
    twitter = TwitterClient()
    replies = twitter.getReplies()
    replies.reverse()
    for reply in replies:
      text = reply['text']
      texts = reply['text'].split()
      #全角スペースに対応
      if len(texts) < 2:
        texts = reply['text'].split(u'　')
      if len(texts) < 2:
        self.response.out.write('<li>[%s] is irregure</li>'%(text)) 
        continue
      keyword = texts[1]
      user    = reply['user']
      #自分のreplyは無視
      if user['screen_name'] == self.username :
        self.response.out.write('<li>[%s] is my status</li>'%(text))
        continue

      #既に処理済みのreplyも無視
      if not Status.isNewStatus( reply['id'] ) :
        self.response.out.write('<li>[%s] is old status</li>'%(text)) 
        continue

      #位置を取得
      finder = LocationFinder()
      loc = finder.find( keyword )
      if not loc:
        #見つからなかった
        mes = self.fail_message%( reply['user']['screen_name'] ,keyword)
      else:
        #見つかった
        mes = self.success_message[loc['type']]%( reply['user']['screen_name'] , loc['title'] , 'L:' + str(loc['lat']) + "," + str(loc['lon']) + ' ' + loc['url'] )

      #返信した内容を保存
      Status.saveStatus( reply,loc,mes )
      #twitterのstatusを更新
      if not debug:
        twitter.sendReply( mes , reply['id'])
      self.response.out.write('<li>[%s]:[%s]</li>'%(keyword,mes) )

    self.response.out.write('</ul>')

  

def main():
  application = webapp.WSGIApplication([('/cron', CronHandler),
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
