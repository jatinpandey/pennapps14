import app
from pymongo import Connection
import string
from googlemaps import GoogleMaps
from pygeocoder import Geocoder

"""
users: {"id":str, "name":str, "age":int, "gender":str, "city":str, zip":str, loc":list, "radius":int, "matches":list} 

	# Matches is a list of events

restaurants: {"id":str, "name":str, "cuisine":list, "pics":str, "address":str, "city":str, "phone":str, "users":list}
	# Users is a list of user docs who like the restaurant

events: {"id":str, "users":list, "restaurant":list} # Add datetime at some point

matches: {"id":{"restaurant_id":list}}
"""

connection = Connection('localhost', 27017) # Will want to change this to real server later on
db = connection['test-database']
users = db['users']
gmaps = GoogleMaps()

def create_users():
	new_user1 = {"id":"1", "name":"Alen", "age":22, "gender":"male", "city":"Pittsburgh", "loc":[40.396258, -79.838659], "radius":20, "matches":[], "zip":15221}
	new_user2 = {"id":"2", "name":"Lara", "age":22, "gender":"female", "city":"Pittsburgh", "loc":[40.443866, -79.942042], "radius":15, "matches":[], "zip":15213}
	users.remove({})
	users.insert(new_user1)
	users.insert(new_user2)
	print "Printing users"
	for u in users.find():
		print u


def create_rests():
	results = app.query_yelp(15221)
	restaurants = db['restaurants']
	restaurants.remove({})
	app.add_to_db(results, restaurants)
	# for r in restaurants.find():
	# 	print r

def get_suggestions():
	for user in users.find():
		explore(db, user['id'])

def explore(db, user_id):
	users = db['users']
	restaurants = db['restaurants']
	user = users.find({'id': user_id})[0]
	user_coords = user['loc']
	dist = user['radius']
	zipcode = user['zip']
	city = user['city']

	# We need to call the Yelp API here to make sure we add anything we don't already have in our database - for now we'll just search by ZIP code
	results = app.query_yelp(zipcode)
	app.add_to_db(results, restaurants)

	# Find restaurants in user's city, then filter by distance based on user's location
	suggestions = restaurants.find({"city":city})
	# print user_coords
	# cur_user_address = Geocoder.reverse_geocode(user_coords[0], user_coords[1])
	# for rest in suggestions:
	# 	rest_ad = rest['address']
	# 	dist_in_meters = gmaps.directions(cur_user_address, rest_ad)['Directions']['Distance']['meters']
	# 	dist_in_miles = 1.609*(float(dist_in_meters) / 1000.0) 
	# 	if dist_in_miles > dist:
	# 		suggestions.remove(rest)

	print "Printing suggestions for user " + str(user_id)
	for s in suggestions:
		print s

if __name__ == "__main__":
	create_users()
	create_rests()
	get_suggestions()