from flask import Flask, render_template, request, url_for
import sys
import urllib
import Image
import flickr

app = Flask(__name__)

@app.route('/')
def main():
	photos = flickr.photos_search(tags="dog",per_page=3)
	urls = []
	for photo in photos:
		urls.append(photo.getURL(size='Medium',urlType='source'))

	print urls
	return render_template("index.html",urls=urls)

if __name__ == "__main__":
	app.debug = True
	app.run()
