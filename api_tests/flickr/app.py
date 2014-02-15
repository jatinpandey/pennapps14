from flask import Flask, render_template, request, url_for
import flickr

app = Flask(__name__)

@app.route('/')
def main():
	photos = flickr.photos_search("dog",3)
	urls = []
	for photo in photos:
		urls.append(photo.getURL(size='Square', urlType='source'))

	return render_template("index.html",urls=urls)

if __name__ == "__main__":
	app.debug = True
	app.run()
