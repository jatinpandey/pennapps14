from flask import Flask, render_template, request
import requests
import oauth2
import urllib
import urllib2
import json

app = Flask(__name__)

@app.route('/')
def main():
	consumer_key = "g3uCx1ffBEd1MnFcapxpAQ" 
	consumer_secret = "9UCPARWyfHw54ooHl_CeyvnXZNE" 
	token = "7Xpo8fE5MPDYbZnao0xf8KS5szH4hduz"
	token_secret = "AaIfeW__93y2k1_aVQH0ESUxV6U"

	url_term = "pizza"
	url_location = "New+Jersey"

	#url = "http://api.yelp.com/v2/search?term=cream+puffs&location=San+Francisco" 
	#url = "http://api.yelp.com/v2/search?term=food&bounds=37.900000,-122.500000|37.788022,-122.399797&limit=3"

	url_bounds = "37.900000,-122.500000|37.788022,-122.399797&limit=3"
	url_term = "food"
	url = "http://api.yelp.com/v2/search?" + "term=" +  url_term + "&" + "bounds=" + url_bounds

	#signing the url
	consumer = oauth2.Consumer(consumer_key,consumer_secret)
	oauth_request = oauth2.Request('GET',url,{})
	oauth_request.update({'oauth_nonce': oauth2.generate_nonce(),
		'oauth_timestamp': oauth2.generate_timestamp(),
		'oauth_token': token,
		'oauth_consumer_key': consumer_key})

	token = oauth2.Token(token, token_secret)
	oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
	signed_url = oauth_request.to_url()
	print 'Signed URL: %s\n' % (signed_url,)

# Connect
	try:
		conn = urllib2.urlopen(signed_url, None)
		try:
			response = json.loads(conn.read())
		finally:
			conn.close()
	except urllib2.HTTPError, error:
		response = json.loads(error.read())

	restaurant_name = response['businesses'][0]['name']

	restaurant_url = response['businesses'][0]['url']
	restaurant_phone = response['businesses'][0]['display_phone']
	restaurant_address = response['businesses'][0]['location']
	print restaurant_address #it works
	restaurant_categories = response['businesses'][0]['categories']


	return render_template("index.html",restaurant_name = restaurant_name, restaurant_url = restaurant_url, restaurant_phone = restaurant_phone, restaurant_address = restaurant_address, restaurant_categories = restaurant_categories)

if __name__ == "__main__":
	app.debug = True
	app.run()
