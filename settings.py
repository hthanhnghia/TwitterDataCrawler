import oauth2
import urllib2

TWITTER_API_KEY = ""
TWITTER_API_SECRET = ""
TWITTER_ACCESS_TOKEN_KEY = ""
TWITTER_ACCESS_TOKEN_SECRET = ""
TWITTER_STREAM_URL = "https://stream.twitter.com/1.1/statuses/filter.json?locations=30,10,150,54" # Twitter stream api url for ASIA Pacific region

OAUTH_TOKEN = oauth2.Token(key=TWITTER_ACCESS_TOKEN_KEY, secret=TWITTER_ACCESS_TOKEN_SECRET)
OAUTH_CONSUMER = oauth2.Consumer(key=TWITTER_API_KEY, secret=TWITTER_API_SECRET)
SIGNATURE_METHOD = oauth2.SignatureMethod_HMAC_SHA1()

HTTP_HANDLER  = urllib2.HTTPHandler(debuglevel=0)
HTTPS_HANDLER = urllib2.HTTPSHandler(debuglevel=0)