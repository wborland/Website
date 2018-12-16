import boto3
import db

def queryAll(query):
    conn = db.conn()

    cursor = conn.cursor()
    cursor.execute(query)

    conn.commit()
    conn.close()
    
    return cursor.fetchall()

def queryOne(query):
    conn = db.conn()

    cursor = conn.cursor()
    cursor.execute(query)

    conn.commit()
    conn.close()
    
    return cursor.fetchone()

def addEntry(name, file, position):
    conn = db.conn()

    cursor = conn.cursor()
    cursor.execute(""" INSERT INTO `website`.`intern` (`name`, `file`, `position`) VALUES (%s, %s, %s);""", [name, file, position])

    conn.commit()
    conn.close()


def updateStatusNum(id, type):
    conn = db.conn()

    cursor = conn.cursor()
    cursor.execute("""update website.intern set status_num = """ + type + """ where id = """ + id)

    conn.commit()
    conn.close()


def updateStatus(id, status):
    conn = db.conn()

    cursor = conn.cursor()
    cursor.execute("""update website.intern set status = \"""" + status + """\" where id = """ + id)

    conn.commit()
    conn.close()

