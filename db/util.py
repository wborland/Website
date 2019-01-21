import boto3
import db
import time

def queryAll(query):
    conn = db.conn()
    cursor = conn.cursor()

    cursor.execute(query)
    conn.commit()
    all = cursor.fetchall()

    conn.close()
    cursor.close()

    return all

def queryOne(query):
    conn = db.conn()
    cursor = conn.cursor()

    cursor.execute(query)
    conn.commit()
    one = cursor.fetchone()

    conn.close()
    cursor.close()
    
    return one


def getAdmin():

    conn = db.conn()
    cursor = conn.cursor()
    cursor.execute("SELECT status_num, had_interview FROM website.intern")
    
    obj = cursor.fetchall()
    entrys,interviews,offers = 0,0,0

    for l in obj:
        entrys += 1
        if l[0] == 3:
            offers += 1
        if l[1] == 1:
            interviews += 1

    conn.close()
    cursor.close()

    return entrys,interviews,offers

def addEntry(name, file, position):
    conn = db.conn()

    cursor = conn.cursor()
    cursor.execute(""" INSERT INTO `website`.`intern` (`name`, `file`, `position`) VALUES (%s, %s, %s);""", [name, file, position])

    conn.commit()
    conn.close()


def updateEntry(id, status, num, notes):
    conn = db.conn()
    cursor = conn.cursor()

    if num == "1":
        cursor.execute("""update website.intern set status = \"""" + status + """\", status_num = """  + num + """, notes =\"""" + notes + """\" , had_interview = 1 where id = """ + id)
    else:
        cursor.execute("""update website.intern set status = \"""" + status + """\", status_num = """  + num + """, notes = \"""" + notes + """\" where id = """ + id)
    
    conn.commit()
    conn.close()

