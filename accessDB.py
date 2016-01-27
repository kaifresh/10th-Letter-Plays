import MySQLdb

def accessDatabase():
    db = MySQLdb.connect(host="database.turnup.club", # your host, usually localhost
                         user="XXXX", # your username
                          passwd="XXXX", # your password
                          db="jplay") # name of the data base

    print "accessed database!", db
    return db

def closeConnection(db):
    db.close()