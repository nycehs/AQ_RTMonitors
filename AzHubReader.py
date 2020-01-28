#!/usr/local/bin/python3.6

# import serial
import FakeSerial as serial
import socket
import datetime
import time
import os
import sys
import sqlite3


class Database:
    """By Amir Hassan Azimi [http://parsclick.net/]"""
    def __init__(self, **kwargs):
        self.filename = kwargs.get('filename')
        self.table = kwargs.get('table', 'airquality')

    def sql_do(self, sql, *params):
        self._db.execute(sql, params)
        self._db.commit()

    def insertrow(self, row):
        self._db.execute('insert into {} (t1, i1) values (?, ?)'.format(self._table), (row['t1'], row['i1']))
        self._db.commit()

    def insert(self, sqlstr):
        sql = "INSERT INTO DOHSensor(EventData) VALUES('" + str(sqlstr) + "');"
        self._db.execute(sql)
        self._db.commit()

    def retrieve(self, key):
        cursor = self._db.execute('select * from {} where t1 = ?'.format(self._table), (key,))
        return dict(cursor.fetchone())

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
        self._db = sqlite3.connect(fn)
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


class SerialWrapper:
    def __init__(self, device):
        self.comm = serial.Serial(device, 19200)

    def open(self): 
        ''' Open the serial port.'''
        self.comm.open()
        self.comm.write(bytes('sd on\r', 'utf-8'))

    def custom_readline(self):
        rdg = ''
        ch = self.comm.read()
 
        while ch.decode('utf-8', errors='ignore') != '\r':
            rdg = rdg + ch.decode('utf-8', errors='ignore')
            ch = self.comm.read() 
        return rdg

    def return_rdg(self, datafields, hostname):
         timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S.%f')
         readings = hostname + " " + \
             timestamp + " " + \
             datafields[3] + " " + \
             datafields[4] + " " + \
             datafields[5] + " " + \
             datafields[6]
         return readings

    def sendData(self, data):
        data += "\r\n"
        self.comm.write(data.encode())

def main():
    ser = SerialWrapper('COM4')
    db = Database(filename = 'airquality.db', table = 'DOHSensor')
#   ser.open
    ser.open()
    

    while 1:
        datafields = ser.custom_readline().split()
        if len(datafields) == 7:
            readings = ser.return_rdg(datafields, 'testpi')
            print(readings)
            db.insert(readings)
        else:
            print("sleeping")
            time.sleep(5)

if __name__ == "__main__":
    main()
    
