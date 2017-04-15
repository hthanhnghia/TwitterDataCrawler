import re
import os
import urllib2
from log_handler import logger

def byteify(input):
	if isinstance(input, dict):
		return {byteify(key):byteify(value) for key,value in input.iteritems()}
	elif isinstance(input, list):
		return [byteify(element) for element in input]
	elif isinstance(input, unicode):
		return input.encode('utf-8')
	else:
		return input

def is_youtube_url(url):
	pattern1 = r'youtu\.be'
	pattern2 = r'youtube\.com\/watch'
	p1 = re.findall(pattern1, url)
	p2 = re.findall(pattern2, url)
	return len(p1) + len(p2) > 0 

def is_instagram_url(url):
	pattern = r'(instagr\.am/p/.*|instagram\.com/p/.*)'
	p = re.findall(pattern, url)
	return len(p) > 0

def write_text_data(directory, file_name, text_data):
	if not os.path.exists(directory):
		os.makedirs(directory)

	with open(directory + "/" + file_name, "a+") as output_file:
		output_file.write(text_data+"\n")

	output_file.close()

def download_file(url, directory, file_name):
  try:
    if not os.path.exists(directory):
      os.makedirs(directory)

    file_content = urllib2.urlopen(url).read()

    with open(directory + "/" + file_name,'wb') as file_output:
      file_output.write(file_content)

    return True

  except urllib2.HTTPError, e:
    logger.error('HTTPError: ' + str(e.code) + ', URL: ' + url)
    return False
  except urllib2.URLError, e:
    logger.error('URLError: ' + str(e.reason) + ', URL: ' + url)
    return False
  except httplib.HTTPException, e:
    logger.error('HTTPException' + ', URL: ' + url)
    return False
  except Exception:
    logger.error('Generic exception: ' + traceback.format_exc() + ', URL: ' + url)
    return False