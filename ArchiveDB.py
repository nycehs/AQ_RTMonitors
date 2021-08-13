import os
import shutil
import sqlite3
from sqlite3 import Error
from configparser import ConfigParser
from datetime import datetime

def createDOHSensorTable():
    sqlcmd = """CREATE TABLE IF NOT EXISTS DOHSensor 
                (
                        ID integer NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                        EventData text NOT NULL
                );"""
    return sqlcmd

def createSyncTable():
    sqlcmd = """CREATE TABLE IF NOT EXISTS SyncTable
                (
                        LastID integer
                );"""
    return sqlcmd

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file, isolation_level=None)
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn
    except Error as e:
        print(e)
 
    return None

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def archiveDB(locationid):
    now = datetime.now()
    source_dir = "/home/pi/Database"
    dest_dir = "/home/pi/DatabaseArchive/" + \
    locationid + \
    now.strftime("_%Y%m%d_%H%M")

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    for file in os.listdir(source_dir):
        fullpath = os.path.join(source_dir, file)
        shutil.move(fullpath,dest_dir)

def openini(inifile):
    config = ConfigParser()
    config.read(inifile)
    locationid = config.get('location', 'locationid')
    return locationid

def main():
    cfgfile = '/usr/local/bin/AzHubService/AzHubReader.ini'
    locid = openini(cfgfile)    
    airqualdb = "/home/pi/Database/airquality.db"
    syncdb =  "/home/pi/Database/airqualitysync.db"
    archiveDB(locid)

    sqlcmd_airqual = createDOHSensorTable()
    sqlcmd_sync = createSyncTable()

    connaq = create_connection(airqualdb)
    if connaq is not None:
        create_table(connaq, sqlcmd_airqual)
    else:
        print("Error! cannot create the airquality database connection.")

    connaqs = create_connection(syncdb)
    if connaqs is not None:
        create_table(connaqs, sqlcmd_sync)
        connaqs.execute('INSERT INTO SyncTable(LastId) VALUES(1);')
    else:
        print("Error! cannot create the airqualitysync database connection.")

if __name__ == '__main__':
    main()

