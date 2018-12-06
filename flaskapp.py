from flask import Flask, render_template, request, send_file, send_from_directory, redirect, url_for, session, jsonify, Response, make_response
from werkzeug.utils import secure_filename
from flasgger import Swagger
import os
import db
import boto3
import uuid
import datetime

app = Flask(__name__)

if os.environ.get('circle') is None:
	app.config.from_pyfile('../config.cfg')
else:
	app.config['PASSWORD'] = os.environ.get('PASSWORD')
	app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


if 'SWAGGER' in app.config:
	Swagger(app)

@app.route('/s3')
def s3():
	s3 = boto3.resource('s3')

	data = open('Will_Borland_Resume.pdf', 'rb')
	s3.Bucket(app.config['S3UPLOAD']).put_object(Key=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), Body=data)

	return "Good"

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
def upload():
	s3 = boto3.resource('s3')
	f = request.files['file']
	name = request.form['name']
	position = request.form["position"]

	fileName =  str(uuid.uuid4()) + "." + f.filename.rsplit('.', 1)[1].lower()
	s3.Bucket(app.config['S3UPLOAD']).put_object(Key=fileName, Body=f)

	add_entry_cmd = """ INSERT INTO `website`.`intern` (`name`, `file`, `position`) VALUES (%s, %s, %s);"""
	conn = db.conn()
	cursor = conn.cursor()
	cursor.execute(add_entry_cmd, [name, fileName, position])
	conn.commit()


	return redirect(url_for('intern'))

@app.route('/admin')
def admin():
	if 'intern' in session and session['intern'] == 'ok':
		return render_template('admin.html')
	else:
		session['redirect'] = 'admin'
		return redirect(url_for('login'))

@app.route('/login', methods=['POST', 'GET'])
def login():

	if 'password' in request.form:
		if app.config['PASSWORD'] == request.form['password']:
			if 'redirect' in session:
				response = make_response(redirect(url_for(session['redirect'])))
				session.pop('redirect', None)
				session['intern'] = 'ok'
				return response
			else:
				session['intern'] = 'ok'
				return redirect(url_for('index'))
		else:
			return render_template('login.html', message="Incorrect Password")
	else:
		return render_template('login.html')


@app.route('/intern', defaults=({'error': None}))
def intern(error):
	if 'intern' in session and session['intern'] == 'ok':
		conn = db.conn()
		cursor = conn.cursor()
		md = """SELECT * from `website`.`intern`"""
		cursor.execute(md)
		conn.commit()
		out = cursor.fetchall()

		return render_template('intern.html', files=out, error=error)
	else:
		session['redirect'] = 'intern'
		return redirect(url_for('login'))


@app.route('/entry/<id>')
def entry(id):
	if 'intern' in session and session['intern'] == 'ok':
		conn = db.conn()
		cursor = conn.cursor()
		md = """SELECT * from `website`.`intern` WHERE id =""" + id
		cursor.execute(md)
		conn.commit()
		entry = cursor.fetchone()

		if os.path.isfile(app.config['FILEPATH'] + entry[2]):
			return render_template('entry.html', entry=entry, file=entry[2])
		else:
			try:
				s3 = boto3.resource('s3')
				s3.Bucket(app.config['S3UPLOAD']).download_file(entry[2], app.config['FILEPATH'] + entry[2])
				return render_template('entry.html', entry=entry, file=entry[2])
			except:
				return render_template('entry.html', entry=entry, file=-1)
	else:
		return redirect(url_for('login'))


@app.route('/file/<file>')
def getFile(file):

	if os.path.isfile(app.config['FILEPATH'] + file):
		return send_file(app.config['FILEPATH'] + file)
	else:
		return render_template('404.html')


@app.route('/updateStatus/<type>/<id>', methods = ['POST'])
def update(type, id):
	if 'intern' in session and session['intern'] == 'ok':
		conn = db.conn()
		cursor = conn.cursor()
		md = """update website.intern set status_num = """ + type + """ where id = """ + id
		cursor.execute(md)
		conn.commit()

		return redirect(url_for('intern'))
	else:
		return redirect(url_for('login'))


@app.route('/editStatus', methods = ['POST'])
def edit():
	if 'intern' in session and session['intern'] == 'ok':
		entry = request.form["entry"]
		new = request.form["new"]
		
		conn = db.conn()
		cursor = conn.cursor()
		md = """update website.intern set status = \"""" + new + """\" where id = """ + entry

		cursor.execute(md)
		conn.commit()

		return "Ok"
	else:
		return "Error"


@app.route('/quiz/science')
def science():
	science = {
		"Which kind of waves are used to make and receive cellphone calls?" : [
			"Radio waves",
			"Visible light waves",
			"Sound waves",
			"Gravity waves"
		],
		"What does a light-year measure?" : [
			"Distance",
			"Brightness",
			"Time",
			"Weight"
		],
		"hypothesis": [
			"A proposed, scientifically testable explanation for an observed phenomenon.",
			"Information that has been objectively verified through direct observation",
			"A concept based on scientific laws and axioms (rules assumed to be true and valid) where general agreement is present.",
			"The combination of components and processes that serve a common function."
		]

	}

	return jsonify(science)

@app.route('/quiz/trivia')
def trivia():
	trivia = {
		"Who directed Star Wars?" : [
			"George Lucas",
			"Steven Spielberg",
			"Robert Zemeckis",
			"Francis Ford Coppola"
		],
		"What is a group of Crows called?" : [
			"Murder",
			"Flock",
			"Swarm",
			"Gaggle"
		],
		"What is Earth's largest continent?" : [
			"Asia",
			"North America",
			"Africa",
			"Antarctica"
		]
	}

	return jsonify(trivia)


@app.route("/quiz/math")
def math():
	math = {
		"What is the area of a triangle with sides 13 and 8" : [
			"52",
			"64",
			"48",
			"71"
		],
		"What is 20 percent off of 30 dollars?" : [
			"$6",
			"$10",
			"$7",
			"$5"
		],
		"30 is 60% of what number?" : [
			"50",
			"55",
			"45",
			"60"
		]
	}

	return jsonify(math)

@app.route("/test")
def test():
	return render_template('test.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html')

@app.after_request
def addHeaders(response):
	response.headers['Content-Security-Policy'] = "object-src 'self';script-src 'nonce-c3lzdGVtc2dvZA' https://ajax.googleapis.com https://www.googletagmanager.com https://code.jquery.com https://cdnjs.cloudflare.com https://stackpath.bootstrapcdn.com https://maxcdn.bootstrapcdn.com https://cdn.datatables.net 'self' ; frame-ancestors 'self'; style-src 'self' https://stackpath.bootstrapcdn.com https://cdnjs.cloudflare.com https://cdn.datatables.net https://code.jquery.com https://maxcdn.bootstrapcdn.com https://use.fontawesome.com; font-src https://cdnjs.cloudflare.com https://use.fontawesome.com 'self'"
	response.headers['Strict-Transport-Security'] = "max-age=63072000; includeSubDomains; preload"
	response.headers['X-Frame-Options'] = "SAMEORIGIN"
	return response

if __name__ == '__main__':
  app.run(debug=True)
