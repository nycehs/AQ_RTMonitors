import base64

class Database:
    
    def __init__(self, **kwargs):
        self.filename = kwargs.get('filename')
        self.table = kwargs.get('table', 'airquality')
        print('In Database Class init method:', self.filename, self.table)


db1 = Database(filename = 'airquality.db', table = 'DOHSensor')
print('In Main method:', db1.filename, db1.table)
print
db2 = Database(filename = 'DOHSensor.db')
print('In Main method:', db2.filename, db2.table)
userid = b'rcalandra'
userid64 = base64.b64encode(userid)
print('userid64 = ', userid64)
userid2 = base64.b64decode(userid64)
print('userid2 = ', userid2)
userid64str = base64.encodestring(userid)
print('userid64str = ', userid64str)
userid3 = base64.decodestring(userid64str)
print('userid3 = ', userid3)


 
