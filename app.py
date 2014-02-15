from flask import Flask, render_template, request
from pymongo import Connection
from googlemaps import GoogleMaps
from pygeocoder import Geocoder
import requests
import json
import oauth2
import urllib
import urllib2

app = Flask(__name__)
connection = Connection('localhost', 27017) # Will want to change this to real server later on
db = connection['database']

"""
IMPORTANT: this is what the schemas for each collection (table) in the database will look like

users: {"id":str, "name":str, "age":int, "gender":str, "city":str, zip":str, loc":list, "radius":int, "matches":list} 

	# Matches is a list of events

restaurants: {"id":str, "name":str, "cuisine":list, "pics":str, "address":str, "city":str, "phone":str, "users":list}

	# String which is value of dir is directory where the pictures ares
	# Users is a list of user docs who like the restaurant

events: {"id":str, "users":list, "restaurant":list} # Add datetime at some point

matches: {"id":{"restaurant_id":list}}

"""

@app.route('/')
def main():
	hello = "helloworld"
	return render_template('index.html', hello=hello)

@app.route('/explore/<user_id>')
def explore():
	users = db['users']
	restaurants = db['restaurants']
	user = users.find({'id': user_id})[0]
	user_coords = user['loc']
	dist = user['radius']
	zipcode = user['zip']
	city = user['city']

	# We need to call the Yelp API here to make sure we add anything we don't already have in our database - for now we'll just search by ZIP code
	results = query_yelp(zipcode)
	add_to_db(results, restaurants)

	# Find restaurants in user's city, then filter by distance based on user's location
	suggestions = restaurants.find({"city":city})
	cur_user_address = Geocoder.reverse_geocode(user_coords[0], user_coords[1])
	for rest in suggestions:
		rest_ad = rest['address']
		dist_in_meters = GoogleMaps.directions(cur_user_address, rest_ad)['Directions']['Distance']['meters']
		dist_in_miles = 1.609*(float(dist_in_meters) / 1000.0) 
		if dist_in_miles > dist:
			suggestions.remove(rest)

	## To-do: pass values from database to emplate
	return render_template('explore.html')

# Purely for testing the explore ui
@app.route('/exploretest')
def exploretest():
	return render_template('explore.html')

@app.route('/matches/<user_id>')
def matches():
	# Returns event IDs in which user has been groped
	user_matches = events.find({'users' : {"$in" : [user_id]}})

	return render_template('matches.html')

# Add results from Yelp which aren't in the database to the DB
def add_to_db(results, restaurants):
	for result in results:
		(r_name, r_url, r_phone, r_address, r_city, r_categories)
		r_name = result[0]
		hit = restaurants.find({'name' : {"$exists" : True, "$in" : [r_name]}})
		# This means this restaurant is in the DB
		if hit.count() != 0:
			continue
		else:
			new_entry = {"id": gen_rand_string(), "name":r_name, "cuisine":result[1], "pics":"", "address":result[3], "city":result[4], "phone":result[2], "users":[]}
			restaurants.insert(new_entry)

def query_yelp(zipcode):
	consumer_key = "g3uCx1ffBEd1MnFcapxpAQ" 
	consumer_secret = "9UCPARWyfHw54ooHl_CeyvnXZNE" 
	token = "7Xpo8fE5MPDYbZnao0xf8KS5szH4hduz"
	token_secret = "AaIfeW__93y2k1_aVQH0ESUxV6U"

	url_term = "food" # Generic search for food
	url = "http://api.yelp.com/v2/search?" + "term=" +  url_term + "&" + "location=" + zipcode

	# Signing the url
	consumer = oauth2.Consumer(consumer_key,consumer_secret)
	oauth_request = oauth2.Request('GET',url,{})
	oauth_request.update({'oauth_nonce': oauth2.generate_nonce(),
		'oauth_timestamp': oauth2.generate_timestamp(),
		'oauth_token': token,
		'oauth_consumer_key': consumer_key})

	token = oauth2.Token(token, token_secret)
	oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
	signed_url = oauth_request.to_url()
	# print 'Signed URL: %s\n' % (signed_url,)

	# Connect
	try:
		conn = urllib2.urlopen(signed_url, None)
		try:
			response = json.loads(conn.read())
		finally:
			conn.close()
	except urllib2.HTTPError, error:
		response = json.loads(error.read())

	# Get and return hits
	result_list = []
	for i in range(len(response['businesses'])):
		bus = response['businesses'][i]
		r_name = bus['name']
		r_url = bus['url']
		r_phone = bus['display_phone']
		r_address = bus['location']
		r_city = r_address['city']
		r_categories = bus['categories']
		result_list.append((r_name, r_url, r_phone, r_address, r_city, r_categories))

	return result_list

def gen_rand_string():
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))

if __name__ == "__main__":
	app.debug = True
	app.run()



