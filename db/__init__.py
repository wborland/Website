from flask import g

import MySQLdb as sql
from MySQLdb.cursors import DictCursor



def make_conn():
    return sql.connect(host="website.czubge8ebda6.us-east-1.rds.amazonaws.com", db="website", passwd="willwebsite",user="will")

    
def conn():
    if not hasattr(g, 'db_conn'):
        g.db_conn = make_conn()

    return g.db_conn
