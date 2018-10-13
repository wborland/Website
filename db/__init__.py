from flask import g

import MySQLdb as sql
from configparser import SafeConfigParser
import os

from MySQLdb.cursors import DictCursor

def make_conn():
   
	parser = SafeConfigParser()

	if os.path.isfile('/home/ubuntu/database.ini'):
		path = '/home/ubuntu/database.ini'
	else:
		path = '../database.ini'

	parser.read(path)

	return sql.connect(
    	host=parser.get('database','host'), 
    	db=parser.get('database','name'),
    	passwd=parser.get('database','pass'),
    	user=parser.get('database','user'))

    
def conn():
    if not hasattr(g, 'db_conn'):
        g.db_conn = make_conn()

    return g.db_conn
