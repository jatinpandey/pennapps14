from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)

@app.route('/')
def main():
	hello="helloworld"
	return render_template('index.html', hello=hello)

@app.route('/explore')
def explore():
	#MONGO: project[palcename, numvotes](results)

	return render_template('explore.html')

@app.route('/matches')
def matches():
	#MONGO: project[palcename, numvotes](results)

	return render_template('matches.html')

if __name__ == "__main__":
	app.debug=True
	app.run()



