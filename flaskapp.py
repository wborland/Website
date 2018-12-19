from flask import Flask, render_template, request, send_file, send_from_directory, redirect, url_for, session, jsonify, Response, make_response, Blueprint
from werkzeug.utils import secure_filename
from flasgger import Swagger
from intern.intern import intern

import os
import db.util
import boto3
import uuid
import datetime
import pdfkit
import requests
import threading
import auth
import socket
import time



app = Flask(__name__)
app.register_blueprint(intern)

if os.environ.get('circle') is None:
	app.config.from_pyfile('../config.cfg')
else:
	app.config['PASSWORD'] = os.environ.get('PASSWORD')
	app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

if 'SWAGGER' in app.config:
	Swagger(app)


@app.route('/')
def index():
	"""
	This is the index page
    ---
    responses:
      501:
        description: Server Error
      200:
	  	description: Index page
    """
	return render_template("index.html")

@app.route('/admin')
@auth.required
def admin():

	admin = db.util.getAdmin()

	return render_template("admin.html", c = socket.gethostname(), n = admin[0][0], i = admin[1][0])

@app.route('/resume')
def resume():
    return send_file("static/resume.pdf")

@app.route('/login', methods=['POST', 'GET'])
def login():
	if 'password' in request.form:
		if app.config['PASSWORD'] == request.form['password']:
			session['intern'] = 'ok'

			if 'redirect' in session:
				url = session['redirect']
				session.pop('redirect', None)
				return redirect(url_for(url))
			else:
				return redirect(url_for('index'))
		else:
			return render_template('login.html', message="Incorrect Password")
	else:
		return render_template('login.html')


@app.route('/file/<file>')
@auth.required
def getFile(file):
	if os.path.isfile(app.config['FILEPATH'] + file):
		return send_file(app.config['FILEPATH'] + file)
	else:
		return render_template('404.html')


@app.route("/test")
@auth.required
def test():
	#thread = threading.Thread(target=processesPage, args=('https://arriscareers.taleo.net/careersection/ex/jobdetail.ftl?job=18002563&tz=GMT-05:00',))
	#thread.start()
	session.clear()
	return "Clear Session"

	#data = db.util.queryAll("""SELECT * from `website`.`intern`""")
	#return render_template('intern.html', files=data)



def processesPage(url):
	r = requests.get(url)
	pdfkit.from_url(url, 'out.pdf')

	print("DONE")
	return

@app.route("/robots.txt")
def robots():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'robots.txt')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html')

@app.after_request
def addHeaders(response):
	response.headers['Content-Security-Policy'] = "object-src 'self';script-src 'nonce-c3lzdGVtc2dvZA' https://ajax.googleapis.com https://www.google-analytics.com/analytics.js https://www.googletagmanager.com/gtag/ https://code.jquery.com https://cdnjs.cloudflare.com https://stackpath.bootstrapcdn.com https://maxcdn.bootstrapcdn.com https://cdn.datatables.net 'self' ; frame-ancestors 'self'; style-src 'self' https://stackpath.bootstrapcdn.com https://cdnjs.cloudflare.com https://cdn.datatables.net https://code.jquery.com https://maxcdn.bootstrapcdn.com https://use.fontawesome.com; font-src https://cdnjs.cloudflare.com https://use.fontawesome.com 'self'"
	response.headers['Strict-Transport-Security'] = "max-age=63072000; includeSubDomains; preload"
	response.headers['X-Frame-Options'] = "SAMEORIGIN"
	response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	return response
	

if __name__ == '__main__':
  app.run(threaded=True, processes=4)
