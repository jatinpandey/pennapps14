from flask import Flask, render_template, request
from pymongo import Connection
import requests
import json

app = Flask(__name__)
connection = Connection('localhost', 27017) # Will want to change this to real server later on
db = connection['database']

"""
IMPORTANT: this is what the schemas for each collection (table) in the database will look like

users: {"id":str, "name":str, "age":int, "gender":str, "loc":list, "radius":int, "matches":list} 

	# Matches is a list of events

restaurants: {"id":str, "name":str, "cuisine":str, "pics":str, "address":str, "phone":str, "loc":list, "users":list}

	# String which is value of dir is directory where the pictures ares
	# Users is a list of user docs who like the restaurant

events: {"id":str, "users":list, "restaurant":list, "time":datetime}

matches: {"id":{"restaurant_id":list}}

"""

@app.route('/')
def main():
	hello = "helloworld"
	return render_template('index.html', hello=hello)

@app.route('/explore/<user_id>')
def explore():
	users = db['user']
	restaurants = db['restaurants']
	user = users.find({'id': user_id})[0]
	user_coords = user['loc']
	dist = user['radius']
	# In addition to this, we need to call the Yelp API here to make sure we add anything we don't already have in our database
	suggestions = restaurants.find({"loc": {"$within": {"$center": [user_coords, dist]}}})
	## To-do: add Mongo values to the template
	return render_template('explore.html')

#purely for testing the explore ui
@app.route('/exploretest')
def exploretest():
	return render_template('explore.html')

@app.route('/matches/<user_id>')
def matches():
	users = db['users']
	user_matches = users.find({'user_id':user_id})[0]['matches']

	return render_template('matches.html')

if __name__ == "__main__":
	app.debug = True
	app.run()



