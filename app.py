#!/user/bin/python2.7
# App to capture data from twitter stream
from twython import Twython
from credentials import *
import psycopg2
import urllib2
from twython import TwythonStreamer
import webbrowser
import time
import datetime

stop = "1/15/2017 19:13:00"
stoptime = datetime.datetime.strptime(stop, "%m/%d/%Y %H:%M:%S")
boundingbox = '-77.577357,38.607025,-76.664004,39.192539'


constring = "dbname='%s' user='%s' host='%s' password='%s'" %(dbname, user, host, password)

try:
	con = psycopg2.connect(constring)
	print "Connected to %s" % dbname
except:
	print "I am unable to connect to the database"

c = con.cursor()

twitter = Twython(APP_KEY, APP_SECRET)
auth = twitter.get_authentication_tokens()
OAUTH_TOKEN = auth['oauth_token']
OAUTH_TOKEN_SECRET = auth['oauth_token_secret']

url = auth['auth_url']

webbrowser.open(url, 2)

pin = raw_input('Enter PIN: ')

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
final_step = twitter.get_authorized_tokens(pin)

OAUTH_TOKEN = final_step['oauth_token']
OAUTH_TOKEN_SECRET = final_step['oauth_token_secret']

class MyStreamer(TwythonStreamer):
	def on_success(self, data):
		if 'text' in data:
			user = data['user']['name']
			message = data['text']
			message = message.replace("'", "")
			coordinates = data['coordinates']
			if coordinates != None:
				lon = coordinates['coordinates'][0]
				lat = coordinates['coordinates'][1]
				sql = "INSERT INTO test_capture VALUES('%s', '%s', %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))" % (user, message, lon, lat, lon, lat)
				print sql
				try:
					c.execute(sql)
					con.commit()
				except Exception, e:
					print "Couldn't update database"
					print str(e)
					#con.close()
					#con = psycopg2.connect(constring)
					#c = con.cursor()
	def on_error(self, status_code, data):
		print status_code, data


stream = MyStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
while stoptime >= datetime.datetime.now():
	stream.statuses.filter(locations=boundingbox)
con.close()
