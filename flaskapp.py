from flask import Flask, render_template, request, send_file, send_from_directory, redirect, url_for, session, jsonify, Response, make_response
from werkzeug.utils import secure_filename
from flasgger import Swagger
import os
import db.util
import boto3
import uuid
import datetime
import pdfkit
import requests
import threading
import auth

app = Flask(__name__)

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
	
@app.route('/resume')
def resume():
    return send_file("static/resume.pdf")

@app.route('/upload', methods = ['POST'])
@auth.required
def upload():
	s3 = boto3.resource('s3')
	f = request.files['file']
	name = request.form['name']
	position = request.form["position"]

	fileName =  str(uuid.uuid4()) + "." + f.filename.rsplit('.', 1)[1].lower()
	s3.Bucket(app.config['S3UPLOAD']).put_object(Key=fileName, Body=f)

	db.util.addEntry(name, fileName, position)

	return redirect(url_for('intern'))

@app.route('/admin')
@auth.required
def admin():
		return render_template('admin.html')

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


@app.route('/intern', defaults=({'error': None}))
@auth.required
def intern(error):
	out = db.util.queryAll("""SELECT * from `website`.`intern`""")
	return render_template('intern.html', files=out, error=error)



@app.route('/entry/<id>')
@auth.required
def entry(id):
	entry = db.util.queryOne("""SELECT * from `website`.`intern` WHERE id =""" + id)

	print(entry)

	if os.path.isfile(app.config['FILEPATH'] + entry[2]):
		return render_template('entry.html', entry=entry, file=entry[2])
	else:
		try:
			s3 = boto3.resource('s3')
			s3.Bucket(app.config['S3UPLOAD']).download_file(entry[2], app.config['FILEPATH'] + entry[2])
			return render_template('entry.html', entry=entry, file=entry[2])
		
		except:
			return render_template('entry.html', entry=entry, file=-1)

@app.route('/file/<file>')
@auth.required
def getFile(file):

	if os.path.isfile(app.config['FILEPATH'] + file):
		return send_file(app.config['FILEPATH'] + file)
	else:
		return render_template('404.html')


@app.route('/updateStatus/<type>/<id>', methods = ['POST'])
@auth.required
def update(type, id):
	if 'intern' in session and session['intern'] == 'ok':
		db.util.updateStatusNum(id, type)

		return redirect(url_for('intern'))
	else:
		return redirect(url_for('login'))


@app.route('/editStatus', methods = ['POST'])
@auth.required
def edit():

	try:
		entry = request.form["entry"]
		new = request.form["new"]

		print(entry + " " + new)

		db.util.updateStatus(entry, new)

		return "Ok"
	except:
		return "Error"


@app.route("/test")
@auth.required
def test():
	#thread = threading.Thread(target=processesPage, args=('https://arriscareers.taleo.net/careersection/ex/jobdetail.ftl?job=18002563&tz=GMT-05:00',))
	#thread.start()

	data = db.util.queryAll("""SELECT * from `website`.`intern`""")
	return render_template('intern.html', files=data)



def processesPage(url):
	r = requests.get(url)

	options = {
		'encoding': "UTF-8",
		'images': None,
		'enable-forms': None,
		'enable-plugins': None,
		'print-media-type': None
	}

	pdfkit.from_url(url, 'out.pdf', options=options)

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
