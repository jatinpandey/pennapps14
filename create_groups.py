from pymongo import Connection
import json
import random
import string

connection = Connection('localhost', 27017) # Will want to change this to real server later on
db = connection['database']


"""
IMPORTANT: this is what the schemas for each collection (table) in the database will look like

users: {"id":str, "name":str, "age":int, "gender":str, "loc":list, "radius":int, "matches":list} 

	# Matches is a list of events

restaurants: {"id":str, "name":str, "cuisine":str, "pics":str, "address":str, "phone":str, "loc":list, "users":list}

	# String which is value of dir is directory where the pictures ares
	# Users is a list of user docs who like the restaurant

events: {"id":str, "users":list, "restaurant":document} # Add datetime at some point

matches: {"id":{"restaurant_id":list}}

"""

# Very naive user-matching/event creation algorithm - can improve later. Need to install this as a cron job on the server which runs periodically - e.g., every 5 minutes
def main():
	restaurants = db['restaurants'].find()
	events = db['events']
	users_matched = set()
	for r in restaurant:
		users = r['users']
		# This loop ensures that a user isn't matched to two different events
		for uid in users:
			if uid in users_matched:
				users.remove(uid)
		# If there's still enough users for this restaurant, create a new event
		if len(users) > 1:
			# This generates a random event id - very unlikely duplicates will occur - can modify later
			event_id = gen_rand_string()
			events.insert({"id:"event_id, "users":users, "restaurant":r})
			for u in users:
				users_matched.add(u)
	return 0

def gen_rand_string():
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))

if __name__ == "__main__":
	main()
