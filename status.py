# coding=utf-8
#!/usr/bin/env python


from google.appengine.ext import db
import datetime

#受信した発言を保存する
class Status(db.Model):
  #Status ID
  id    = db.IntegerProperty(required=True)
  #Status の中身
  text  = db.TextProperty()
  #Status の作成日
  created_at = db.DateTimeProperty()
  #Status の作成ユーザー
  user_id    = db.IntegerProperty()
  user_name  = db.StringProperty()
  user_screen_name = db.StringProperty()
  user_location = db.StringProperty()
  user_profile_image_url = db.StringProperty()
  #Statusに該当するLocation
  loc_title   = db.StringProperty()
  loc_point   = db.GeoPtProperty()
  loc_level   = db.IntegerProperty()
  loc_url     = db.LinkProperty()
  loc_type    = db.StringProperty()
  #返信した内容
  reply = db.TextProperty()
  #レコードの追加日時
  insert_time = db.DateTimeProperty(auto_now_add=True)

  #発言のIDが新しく受けたものか確認する
  @staticmethod 
  def isNewStatus( id ):
    key = 's' + str( id )
    status = db.get( db.Key.from_path( "Status" , key ) )
    return ( status == None )

  #発言を保存する
  @staticmethod
  def saveStatus( status, loc , reply ):
    key =  's' + str( status['id'] )
    tweet = Status( key_name = key , id = status['id'] )
    tweet.text = status['text']
    tweet.created_at = Status.str2dt( status['created_at'] ) 
    tweet.user_id = int(status['user']['id'])
    tweet.user_name = status['user']['name']
    tweet.user_screen_name = status['user']['screen_name']
    tweet.user_location = status['user']['location']
    tweet.user_profile_image_url = status['user']['profile_image_url']
    if loc:
      tweet.loc_title = loc['title']
      tweet.loc_point = str(loc['lat']) + ',' + str(loc['lon'])
      tweet.loc_url = db.Link(loc['url'])
      tweet.loc_levelt = int(loc['level'])
      tweet.loc_type = loc['type']
    tweet.reply = reply
    tweet.put()
    return tweet

  @staticmethod
  def getStatuses( limit=20 ):
    list = Status.all()
    list.order('-insert_time')
    return list.fetch( limit )

  #Twitter形式の日時を日時オブジェクトへ変換する
  @staticmethod
  def str2dt(str):
    return datetime.datetime.strptime(str, '%a %b %d %H:%M:%S +0000 %Y')



