from flask import Flask, render_template, Blueprint, request, redirect, url_for, session

import flaskapp
import os
import db.util
import auth
import boto3
import uuid

intern = Blueprint('intern', 'intern', url_prefix='/intern')

@intern.route('/', defaults=({'error': None}))
@auth.required
def internIndex(error):
	out = db.util.queryAll("""SELECT * from `website`.`intern`""")
	return render_template('intern.html', files=out, error=error)


@intern.route('/admin')
@auth.required
def admin():
    return render_template('admin.html')


@intern.route('/upload', methods = ['POST'])
@auth.required
def upload():
	s3 = boto3.resource('s3')
	f = request.files['file']
	name = request.form['name']
	position = request.form["position"]

	fileName =  str(uuid.uuid4()) + "." + f.filename.rsplit('.', 1)[1].lower()
	s3.Bucket(flaskapp.app.config['S3UPLOAD']).put_object(Key=fileName, Body=f)

	db.util.addEntry(name, fileName, position)

	return redirect(url_for('intern.internIndex'))

@intern.route('/entry/<id>')
@auth.required
def entry(id):
	entry = db.util.queryOne("""SELECT * from `website`.`intern` WHERE id =""" + id)

	print(entry)

	if os.path.isfile(flaskapp.app.config['FILEPATH'] + entry[2]):
		return render_template('entry.html', entry=entry, file=entry[2])
	else:
		try:
			s3 = boto3.resource('s3')
			s3.Bucket(flaskapp.app.config['S3UPLOAD']).download_file(entry[2], flaskapp.app.config['FILEPATH'] + entry[2])
			return render_template('entry.html', entry=entry, file=entry[2])
		
		except:
			return render_template('entry.html', entry=entry, file=-1)


@intern.route('/updateStatus/<type>/<id>', methods = ['POST'])
@auth.required
def update(type, id):
    db.util.updateStatusNum(id, type)
    return redirect(url_for('intern.internIndex'))


@intern.route('/editStatus', methods = ['POST'])
@auth.required
def edit():
	try:
		entry = request.form["entry"]
		new = request.form["new"]
		db.util.updateStatus(entry, new)

		return "Ok"
	except:
		return "Error"