pennapps14
==========

Repository for our PennApps S14 application (FaceFood?)

###accomplished:
* figured out how to get shit from Yelp. wrote code to transform Yelp results into database entries. 
* wrote a python script which checks the database for potential matches every 5 minutes and creates them. this algorithm is very naive write now, but fine for the demo
* used some geo libraries in order to filter suggestions for the user
* wrote mongo code for storing info we need in the databases - see the comments at the top of the app.py for the schema we're using right now

###broken:
* ~~something happened to bootstrap. the website looks weird now. it wasn't me, lol. anyway, needs to be fixed.~~ **kudos to alex ^__^**

###to-do:
* turns out that we can't rely on yelp for images. it's not in the API and even if we were to scrape them, no guarantee that the images are of food. best to do what Alex suggested and use an image search API (e.g. google) to get generic images of food
* mongo code needs to be tested...actually all the code needs to be tested
* we need to figure out how we're going to get the user location...i think this should be relatively straightforward tho

