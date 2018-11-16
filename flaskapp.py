from flask import Flask, render_template, request, send_file, send_from_directory, redirect, url_for, session, abort, jsonify, Blueprint, Response, make_response
from werkzeug import secure_filename
from botocore.exceptions import ClientError
from flasgger import Swagger

import click
import subprocess
import os
import glob
import db
import boto3

app = Flask(__name__)


app.config['SWAGGER'] = {
    'title': 'Wborland API',
    'uiversion': 3,
	'version': '1.0',
	"specs_route": "/swagger/"
}
Swagger(app)

app.secretKeyFile = os.path.dirname(
    os.path.realpath(__file__)) + "/../secretkey.txt"
app.passwordFile = os.path.dirname(os.path.realpath(__file__)) + "/../pass.txt"

with open(app.secretKeyFile, 'r') as myfile:
    app.secret_key = myfile.read().replace('\n', '')

with open(app.passwordFile, 'r') as myfile:
    internPassword = myfile.read().replace('\n', '')


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

@app.route('/file/<file>')
def getFile(file):
	thisFile = os.path.dirname(os.path.realpath(__file__)) + "/uploads/" + file

	if os.path.isfile(thisFile):
		return send_file(thisFile)
	else:
		return render_template('fileNotFound.html')

@app.route('/upload', methods = ['POST'])
def upload():
	uploadDir = os.path.dirname(os.path.realpath(__file__))

	name = request.form["name"]
	position = request.form["position"]
	print(position)

	f = request.files['file']
	f.save(uploadDir + "/uploads/" + secure_filename(f.filename))
	add_entry_cmd = """ INSERT INTO `website`.`intern` (`name`, `file`, `position`) VALUES (%s, %s, %s);"""

	conn = db.conn()
	cursor = conn.cursor()
	cursor.execute(add_entry_cmd, [name, secure_filename(f.filename), position])
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
		if internPassword == request.form['password']:
			if 'redirect' in session:
				response = make_response(redirect(url_for(session['redirect'])))
				session.pop('redirect', None)
				session['intern'] = 'ok'
				return response
			else:
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
		thisFile = os.path.dirname(os.path.realpath(__file__)) + "/uploads/" + entry[2]

		if os.path.isfile(thisFile):
			return render_template('entry.html', entry=entry, file=thisFile)
		else:
			return render_template('entry.html', entry=entry, file=-1)
	else:
		return redirect(url_for('login'))


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


@app.route("/test")
def test():
	return render_template('test.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

if __name__ == '__main__':
  app.run(debug=True)
