# coding=utf-8
#!/usr/bin/env python

import os
import yaml
from django.utils import simplejson
from google.appengine.api import urlfetch
from django.utils import simplejson
import urllib
import urllib2
import base64
import logging

class TwitterClient:
  config = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r'))

  username = config['twitter_username']
  passwd = config['twitter_password']



  #自分宛の発言を取得する
  def getReplies(self):
    url = 'http://twitter.com/statuses/mentions.json'
    payload = urllib.urlencode({"count": "50" })
    return self.sendRequest( url , payload ,urlfetch.GET )
    
  #Replyしたユーザー一覧
  def getReplyUsers(self):
    replies = self.getReplies()
    users = {}
    for reply in replies:
      users[reply['user']['id']] = reply['user']
    return users

  def getUser(self,user):
    url = 'http://twitter.com/users/show/%s.json'%(user)
    return self.sendRequest( url , {} , urlfetch.GET )


  #発言を返す
  def sendReply(self,message,in_reply_to_status_id = ''):
    url = "http://twitter.com/statuses/update.json" 
    payload = urllib.urlencode({"status": message.encode("utf-8"),
            "in_reply_to_status_id":in_reply_to_status_id}) 
    return self.sendRequest( url , payload )

  #Base64認証付きのリクエストを送信
  def sendRequest(self,url,payload,method=urlfetch.POST):
    base64string = base64.encodestring("%s:%s" % (self.username,self.passwd))[:-1] 
    headers = {"Authorization": "Basic %s" % base64string} 
    result = urlfetch.fetch(url, payload=payload, method=method, headers=headers)
    if result.status_code == 200:
      return simplejson.loads(result.content)
    return None



