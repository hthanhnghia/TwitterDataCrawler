import urllib2
import json
import re
import httplib
import multiprocessing
import pafy
from datetime import datetime
from bs4 import BeautifulSoup
from log_handler import logger
from utils import *
from settings import *

class TwitterDataCrawler(object):
  def __init__(self, *args, **kwargs):
    self.process_manager = multiprocessing.Manager()
    self.twitter_images = self.process_manager.list()
    self.instagram_images = self.process_manager.list()
    self.twitter_videos = self.process_manager.list()
    self.youtube_videos = self.process_manager.list()

  '''
  Construct, sign, and open a twitter request using the credentials above.
  '''
  def __twitterreq(self, url, http_method, parameters):
    req = oauth2.Request.from_consumer_and_token(OAUTH_CONSUMER, token=OAUTH_TOKEN, http_method=http_method, http_url=url, parameters=parameters)
    req.sign_request(SIGNATURE_METHOD, OAUTH_CONSUMER, OAUTH_TOKEN)
    headers = req.to_header()

    if http_method == "POST":
      encoded_post_data = req.to_postdata()
    else:
      encoded_post_data = None
      url = req.to_url()

    opener = urllib2.OpenerDirector()
    opener.add_handler(HTTP_HANDLER)
    opener.add_handler(HTTPS_HANDLER)

    response = opener.open(url, encoded_post_data)
    return response

  def handle_stream_data(self, string_data, json_data):
    screen_name = json_data['user']['screen_name']
    profile_directory = 'stream_data/%s/%s/%s/%s' %(datetime.now().year, datetime.now().month, datetime.now().day, screen_name)
    tweet_directory = profile_directory + "/" + str(json_data['id'])

    write_text_data(tweet_directory, "tweet.txt", string_data)
    
    if 'profile_image_url' in json_data['user']:
      profile_picture_url = json_data['user']['profile_image_url'].replace("_normal", "")
      file_name = profile_picture_url.split('/')[-1]
      self.twitter_images.append({'url' :profile_picture_url,'directory': profile_directory, 'file_name': file_name})

    if 'extended_entities' in json_data:
      if 'media' in json_data['extended_entities']:
        for media in json_data['extended_entities']['media']:
          if media['type'] == 'photo':
            self.twitter_images.append({'url' : media['media_url'],'directory': tweet_directory})

          elif media['type'] == 'video':
            video_details = media['video_info']['variants'][0]
            self.twitter_videos.append({'url' : video_details['url'],'directory': tweet_directory})

    for url in json_data['entities']['urls']:
      if is_instagram_url(url['expanded_url']):
        self.instagram_images.append({'url' : url['expanded_url'],'directory': tweet_directory})

      elif is_youtube_url(url['expanded_url']):
        self.youtube_videos.append({'url' : url['expanded_url'],'directory': tweet_directory})

  '''
  Fetch stream data from twitter, add media content (images, videos) to queues which are processed in multiple processes
  '''
  def get_stream_data(self):
    response = byteify(self.__twitterreq(TWITTER_STREAM_URL, "GET", []))
    
    try:
      for line in response:
        string_data = unicode(line.strip(), 'utf-8')
        json_data = byteify(json.loads(string_data))
        self.handle_stream_data(string_data, json_data)

    except httplib.IncompleteRead as e:
      logger.error("IncompleteRead")

  '''
  Download images from Twitter server
  '''
  def get_twitter_images(self):
    while True:
      if len(self.twitter_images) > 0 :
        twitter_image = self.twitter_images[0]
        url, directory = twitter_image['url'], twitter_image['directory']

        if 'file_name' in twitter_image:
          file_name = twitter_image['file_name']

        else:
          file_name = url.split('/')[-1]
          
        if download_file(url, directory, file_name):
          del self.twitter_images[0]

  '''
  Download videos from Twitter server
  '''
  def get_twitter_videos(self):
    while True:
      if len(self.twitter_videos) > 0 :
        twitter_video = self.twitter_videos[0]
        url, directory = twitter_video['url'], twitter_video['directory']
        file_name = url.split('/')[-1]

        if download_file(url, directory, file_name):
          del self.twitter_videos[0]

  '''
  Download Instagram images embedded in tweets 
  '''
  def get_instagram_images(self):
    while True:
      if len(self.instagram_images) > 0:
        url, directory = self.instagram_images[0]['url'], self.instagram_images[0]['directory']
        del self.instagram_images[0]
        
        try:  
          html = urllib2.urlopen(url).read()
          bs = BeautifulSoup(html, "html.parser")
          pattern = re.compile('window._sharedData = (.*?);')
          for s in bs.findAll('script'):
            if s.string:
              match = pattern.match(s.string)
              if m:
                img_src = json.loads(match.groups()[0])['entry_data']['PostPage'][0]['media']['display_src']
                file_name = img_src.split('/')[-1]
                download_file(img_src, directory, file_name)
        
        except urllib2.HTTPError:
          pass

  '''
  Download Youtube videos embedded in tweets 
  '''
  def get_youtube_videos(self):
    while True:
      if len(self.youtube_videos) > 0 :
        url, directory = self.youtube_videos[0]['url'], self.youtube_videos[0]['directory']
        del self.youtube_videos[0]

        try:
          video = pafy.new(url)
          stream = video.streams[-1]
          file_name = stream.download(filepath=directory, quiet=True)
        except:
          pass
  
  '''
  Multi-processed crawling
  '''
  def crawl(self):
    p1 = multiprocessing.Process(target=self.get_stream_data())
    p1.start()

    p2 = multiprocessing.Process(target=self.get_self.twitter_images())
    p2.start()

    p3 = multiprocessing.Process(target=self.get_self.twitter_videos())
    p3.start()

    p4 = multiprocessing.Process(target=self.get_self.instagram_images())
    p4.start()
    
    p5 = multiprocessing.Process(target=self.get_self.youtube_videos())
    p5.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()

if __name__ == '__main__':
  crawler = TwitterDataCrawler()
  crawler.crawl()