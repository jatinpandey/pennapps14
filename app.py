from flask import Flask, render_template, request
from pymongo import Connection
import requests
import json

app = Flask(__name__)
connection = Connection('localhost', 27017) # Will want to change this to real server later on
db = connection['database']

"""
IMPORTANT: this is what the schemas for each collection (table) in the database will look like

users: {"user_id":int, "firstname":str, "lastname":str, "age":int, "sex":boolean, "loc":list of length 2 - (x, y) coords}

restaurants: {"rest_id":int, "name":str, "type":str, "pics":list of str (file paths), "loc":list of length 2 - (x, y) coords, "phone":int, "address":str, "users":list of user IDs (of users who have liked this restaurant)}

groups: {"event_id": int, "users": list of user IDs who will be participating in this meal, "restaurant":str, "address":str, "loc": (x,y) coordinates}
"""



@app.route('/')
def main():
	hello = "helloworld"
	return render_template('index.html', hello=hello)

@app.route('/explore')
def explore(userid):
	users = db['user']
	restaurants = db['restaurants']
	user = users.find({'user_id': userid})[0]
	user_coords = user['coords'] # Assume this is list of length 2
	dist = user['dist']
	suggestions = restaurants.find({"loc": {"$within": {"$center": [user_coords, dist]}}})

	return render_template('explore.html')

@app.route('/matches')
def matches():
	#MONGO: project[palcename, numvotes](results)

	return render_template('matches.html')

if __name__ == "__main__":
	app.debug=True
	app.run()



