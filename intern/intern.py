from flask import Flask, render_template, Blueprint, request, redirect, url_for, session

import flaskapp
import os
import db.util
import auth
import boto3
import uuid
import threading
import time






intern = Blueprint('intern', 'intern', url_prefix='/intern')

@intern.route('/', defaults=({'error': None}))
@auth.required
def internIndex(error):
	out = db.util.queryAll("""SELECT * from `website`.`intern`""")
	return render_template('intern.html', files=out, error=error)


@intern.route('/addEntry')
@auth.required
def addEntry():
    return render_template('addEntry.html')


@intern.route('/upload', methods = ['POST'])
@auth.required
def upload():
	f = request.files['file']
	name = request.form['name']
	position = request.form["position"]

	if name is None or position is None or f is None:
		return redirect(url_for('intern.internIndex', error="Incorrect Form"))

	s3 = boto3.resource('s3')
	fileName =  str(uuid.uuid4()) + "." + f.filename.rsplit('.', 1)[1].lower()
	s3.Bucket(flaskapp.app.config['S3UPLOAD']).put_object(Key=fileName, Body=f)
	db.util.addEntry(name, fileName, position)

	return redirect(url_for('intern.internIndex'))

@intern.route('/entry/<id>')
@auth.required
def entry(id):
	entry = list(db.util.queryOne("""SELECT * from `website`.`intern` WHERE id =""" + id))
	notes = entry[7].split('\n') if entry[7] is not None else entry[7]


	if os.path.isfile(flaskapp.app.config['FILEPATH'] + entry[2]):
		return render_template('entry.html', entry=entry, file=entry[2], notes=notes)
	else:
		try:
			s3 = boto3.resource('s3')
			s3.Bucket(flaskapp.app.config['S3UPLOAD']).download_file(entry[2], flaskapp.app.config['FILEPATH'] + entry[2])
			return render_template('entry.html', entry=entry, file=entry[2], notes=notes)
		
		except:
			return render_template('entry.html', entry=entry, file=-1)


@intern.route('/updateEntry', methods = ['POST'])
@auth.required
def updateEntry():
	try:
		entry = request.form["entry"]
		statusText = request.form["statusText"]
		statusNum = request.form["statusNum"]
		notes = request.form["notes"]

		db.util.updateEntry(entry, statusText, statusNum, notes)

		return "Ok"
	except Exception as e:
		return str(e)