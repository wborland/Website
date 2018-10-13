from flask import Flask, render_template, request, send_file, send_from_directory, redirect, url_for, session, abort
from werkzeug import secure_filename
from botocore.exceptions import ClientError

import click
import subprocess
import os
import glob
import db
import boto3

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/resume')
def resume():
    return send_file("static/resume.pdf")

@app.route('/file/<file>')
def getFile(file):
	thisFile = os.path.dirname(os.path.realpath(__file__)) + "/uploads/" + file

	return send_file(thisFile)

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
	return render_template('admin.html')

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/loginCheck', methods = ['POST'])
def loginCheck():
	password = request.form["password"]

	if password == "password":
		return redirect(url_for('intern'))
	else:
		return "Bad password"

@app.route('/intern')
def intern():
	conn = db.conn()
	cursor = conn.cursor()
	md = """SELECT * from `website`.`intern`"""
	cursor.execute(md)
	conn.commit()
	out = cursor.fetchall()

	return render_template('intern.html', files=out)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

if __name__ == '__main__':
  app.run(debug=True)
