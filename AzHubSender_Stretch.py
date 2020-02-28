#!/usr/bin/env python3
# pylint: disable=C0111

import socket
import datetime
import time
import os
import sys

import sqlite3
from azure.eventhub import EventData, EventHubClient, Sender
devenv = "prod"

class Database:
    """By Amir Hassan Azimi [http://parsclick.net/]"""
    def __init__(self, **kwargs):
        self.filename = kwargs.get('filename')
        self.table = kwargs.get('table', 'airquality')

    def sql_attach(self, sysdb_file):
        self._db.execute("ATTACH ? AS syncDB", [sysdb_file])
        self._db.commit()

    def selectLastID(self):
        curs = self._db.execute('''SELECT LastID FROM syncDB.SyncTable''')
        lrowID = dict(curs.fetchone())
        return lrowID['LastID']

    def selectMaxID(self):
        curs = self._db.execute('''SELECT MAX(ID) as MaxID FROM main.DOHSensor''')
        maxRowID = dict(curs.fetchone())
        return maxRowID['MaxID']

    def sql_do(self, sql, *params):
        self._db.execute(sql, params)
        self._db.commit()

    def selectkey(self, key):
        curs = self._db.execute('select * from {} where ID = ?'.format(self._table), (key,))
        return dict(curs.fetchone())

    def selectone(self, arg):
        curs = self._db.execute(arg)
        return dict(curs.fetchone())

    def selectmany(self, arg):
        curs = self._db.execute(arg)
        return curs.fetchall()

    def selectReadings(self, lastID, maxID):
        curs = self._db.execute('SELECT ID, EventData FROM main.DOHSensor WHERE ID BETWEEN ? AND ? ORDER BY ID LIMIT 100', (lastID, maxID));
        return curs.fetchall()

    def insertrow(self, row):
        self._db.execute('insert into {} (t1, i1) values (?, ?)'.format(self._table), (row['t1'], row['i1']))
        self._db.commit()

    def insert(self, sqlstr):
        sql = "INSERT INTO DOHSensor(EventData) VALUES('" + str(sqlstr) + "');"
        self._db.execute(sql)
        self._db.commit()

    def updateSync(self, lastID):
        self._db.execute('''UPDATE syncDB.SyncTable SET LastID = ?''', (lastID,))
        self._db.commit()

    def update(self, row):
        self._db.execute(
            'update {} set i1 = ? where t1 = ?'.format(self._table),
            (row['i1'], row['t1']))
        self._db.commit()

    def delete(self, key):
        self._db.execute('delete from {} where t1 = ?'.format(self._table), (key,))
        self._db.commit()

    def disp_rows(self):
        cursor = self._db.execute('select * from {} order by t1'.format(self._table))
        for row in cursor:
            print('  {}: {}'.format(row['t1'], row['i1']))

    def __iter__(self):
        cursor = self._db.execute('select * from {} order by t1'.format(self._table))
        for row in cursor:
            yield dict(row)

    @property
    def filename(self): return self._filename
    @filename.setter
    def filename(self, fn):
        self._filename = fn
        self._db = sqlite3.connect(fn, isolation_level=None)
        self._db.row_factory = sqlite3.Row
    @filename.deleter
    def filename(self): self.close()
    @property
    def table(self): return self._table
    @table.setter
    def table(self, t): self._table = t
    @table.deleter
    def table(self): self._table = 'airquality'

    def close(self):
            self._db.close()
            del self._filename

class HubSender(object):
    sender = ""
    client = ""

    def __init__(self, devenv='doh'):
        """ Create Event Hub Sender """
        if devenv == 'prod':
                ADDRESS = "amqps://doh-airqual-eventhub.servicebus.windows.net/doh-airqual-event-hub-prod"
                USER = "RootManageSharedAccessKey"
                KEY = "1p1aHCJc5IbamvnzlnvUa2wlvXsaJpSAbAORGlPRaQ4="
        elif devenv == "dev":
                ADDRESS = "amqps://az-doh-airqual-eventhub.servicebus.windows.net/az-doh-airqual-eventhub"
                USER = "RootManageSharedAccessKey"
                KEY = "pfWGtB6obtiUCwwAobAAuaq7B9SZSsnpHY6ArEbeS1A="
        self.client = EventHubClient(ADDRESS, debug=False, username=USER, password=KEY)
        self.sender = self.client.add_sender(partition="1")
        self.client.run()

    def senddata(self, readings):
        self.sender.send(EventData(readings))

    def stop(self):
        self.client.stop()

    def __del__(self):
        #self.sender.close
        self.client.stop()

def main():

    sysdb_file = "/home/pi/Database/airqualitysync.db";
    db_file = "/home/pi/Database/airquality.db";
    db = Database(filename = db_file, table = 'DOHSensor')
    db.sql_attach(sysdb_file)
    hub = HubSender(devenv)

    while True:
        lrow = db.selectLastID()
        #print(lrow)
        mrow = db.selectMaxID()
        #print(mrow)
        if lrow < mrow:
            lnext = lrow + 1
            for row in db.selectReadings(lnext, mrow):
                if row != None:
                    print(dict(row))
                    readings = row['EventData'];
                    lrow = row['ID']
                    #print(readings)
                    hub.senddata(readings)
                    db.updateSync(lrow)
                    time.sleep(.3)
                else:
                    print("row is empty")
            db.updateSync(lrow)
                #lrow = lnext
                #mrow = db.selectMaxID()
        else:
            print("endif lrow < mrow, sleep(2)")
            time.sleep(2)
    print("End Loop")
    hub.stop()
    db.close()
    sys.exit(0)

if __name__ == "__main__":
    main()
