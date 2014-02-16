from flask import Flask, render_template, request, url_for
from pymongo import Connection
from googlemaps import GoogleMaps
import flickr
#from pygeocoder import Geocoder
import random
import requests
import json
import oauth2
import urllib
import urllib2
import string

app = Flask(__name__)
connection = Connection('localhost', 27017) # Will want to change this to real server later on
db = connection['test-database']

"""
IMPORTANT: this is what the schemas for each collection (table) in the database will look like

users: {"id":str, "name":str, "age":int, "gender":str, "city":str, zip":str, loc":list, "radius":int, "matches":list, "seen":set} 

	# Matches is a list of events

restaurants: {"id":str, "name":str, "cuisine":list, "pic_url":str, "address":str, "city":str, "phone":str, "users":list}
	# Users is a list of user docs who like the restaurant

events: {"id":str, "users":list, "restaurant":list} # Add datetime at some point

matches: {"id":{"restaurant_id":list}}

"""

@app.route('/')
def main():
	db['restaurants'].remove({})
	hello = "helloworld"
	return render_template('index.html', hello=hello)

@app.route('/explore/<user_id>')
def explore(user_id):
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
	# print user_coords
	# cur_user_address = Geocoder.reverse_geocode(user_coords[0], user_coords[1])
	# for rest in suggestions:
	# 	rest_ad = rest['address']
	# 	dist_in_meters = GoogleMaps.directions(cur_user_address, rest_ad)['Directions']['Distance']['meters']
	# 	dist_in_miles = 1.609*(float(dist_in_meters) / 1000.0) 
	# 	if dist_in_miles > dist:
	# 		suggestions.remove(rest)

	photos = []
	first_rest_name = ""
	first_rest_pic = ""
	no_more = None
	photo_URL_array = {}
	is_first = 1 #1 = true, 0 = false
	final_suggestions = []
	for s in suggestions:
		if s['name'] not in user['seen']:
			final_suggestions.append(s)

	print "Printing suggestions for user " + str(user_id)

	if len(final_suggestions) == 0:
		no_more = "/static/puppy.jpg"

	for s in final_suggestions:
		print "in for"
		user['seen'].append(s['name'])
		if(is_first == 1):
			# iti s the firsto ne!!!
			first_rest_name = s['name']
			f_food = s['cuisine'][0][0] + " food"
			f_photo = flickr.photos_search(tags=f_food,per_page=1)
			for p in f_photo:
				first_rest_pic = p.getURL(size="Medium",urlType="source")
				if first_rest_pic != "":
					is_first = 0
				else:
					is_first = 1
		else:
			s_name = s['name']
			print s_name
			s_food = s['cuisine'][0][0] + " food"
			print s_food
			photo = flickr.photos_search(tags=s_food,per_page=1)

			for p in photo:
				photo_URL = p.getURL(size="Medium",urlType="source")
				print photo_URL
				if photo_URL != "":
					print photo_URL
					photo_URL_array[s_name] = photo_URL


	for key,value in photo_URL_array.items():
		print "key is " + key + " value is " + value

	users.save(user)

	## To-do: pass values from database to template
	return render_template('explore.html',photo_URL_array = photo_URL_array,first_rest_name = first_rest_name, first_rest_pic = first_rest_pic, no_more = no_more)

# Purely for testing the explore ui
@app.route('/exploretest')
def exploretest():
	return render_template('explore.html',photo_URL_array={})

@app.route('/matches/<user_id>')
def matches():
	# Returns event IDs in which user has been grouped
	user_matches = events.find({'users' : {"$in" : [user_id]}})

	return render_template('matches.html')

# Add results from Yelp which aren't in the database to the DB
def add_to_db(results, restaurants):
	for result in results:
		r_name = result[0]
		hit = restaurants.find({'name' : {"$exists" : True, "$in" : [r_name]}})
		# This means this restaurant is in the DB
		if hit.count() != 0:
			print hit.count()
			continue
		else:
			new_entry = {"id": gen_rand_string(), "name":r_name, "cuisine":result[5], "pics":"", "address":result[3], "city":result[4], "phone":result[2], "users":[]}
			print "##############"
			print result[5]
			print "##############"
			restaurants.insert(new_entry)

def query_yelp(zipcode):
	consumer_key = "g3uCx1ffBEd1MnFcapxpAQ" 
	consumer_secret = "9UCPARWyfHw54ooHl_CeyvnXZNE" 
	token = "7Xpo8fE5MPDYbZnao0xf8KS5szH4hduz"
	token_secret = "AaIfeW__93y2k1_aVQH0ESUxV6U"

	url_term = "food" # Generic search for food
	url = "http://api.yelp.com/v2/search?" + "term=" +  url_term + "&" + "location=" + str(zipcode)

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
		r_name = ""
		r_url = ""
		r_phone = ""
		r_address = ""
		r_city = ""
		r_categories = ""

		if 'name' in bus:
			r_name = bus['name']
		if 'url' in bus:
			r_url = bus['url']
		if 'display_phone' in bus:
			r_phone = bus['display_phone']
		if 'location' in bus:
			r_address = bus['location']
		if 'city' in r_address:
			r_city = r_address['city']
		if 'categories' in bus:
			r_categories = bus['categories']

		result_list.append((r_name, r_url, r_phone, r_address, r_city, r_categories))

	return result_list

def gen_rand_string():
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))

# Purely for testing the explore ui
@app.route('/login')
def loginpage():
	users = db['users']
	restaurants = db['restaurants']
	user = users.find({'id': user_id})[0]
	if (pwd != ""):
		return redirect_internal('matches.html', user_id)
	else:
		return render_template('login.html', user_id, pwd)

def try_to_add_user(username, gender, name, city, age):
	hit = users.find({'id': {"$exists" : True, "$in" : [username]}})
	if hit.count() == 0:
		new_entry = {"id": username, "name":name, "age":age, "gender":gender, "city":city, "zip":"", "loc":{}, "radius":0, "matches":{}, "seen":{} }
		users.insert(new_entry)	
	
@app.route('/signup')
def signuppage():
	users = db['users']
	username = users['id']
	city = users['city']
	name = users['name']
	gender = users['gender']
	age = users['age']
	try_to_add_user(user, gender, name, city, age)
	return render_template('create.html',photo_URL_array = photo_URL_array,first_rest_name = first_rest_name, first_rest_pic = first_rest_pic, no_more = no_more)

	
	
	
	

if __name__ == "__main__":
	app.debug = True
	app.run()


"""
To query mongo: the database is called db
There are three collections (tables): users, restaurants, events
You access them as db[collection_name] e.g. db["users"]
To iterate through a collection, just say:
for thing in collection.find():
	and then, to get attributes, say thing[attribute], e.g. thing["cuisine"] if it's the restaurant collection

"""

