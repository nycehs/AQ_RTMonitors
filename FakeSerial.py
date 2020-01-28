from random import randrange
from random import randint

class Serial(object):

    def __init__(self, DevStr, rate):

        self.timestamp = 'x'
        self.reading3 = 'x'
        self.reading4 = 'x'
        self.pm25 = 40.0
        self.temp = 35
        self.humidity = 10
        self.pressure = 760
        self.output = ""
        self.device = DevStr
        self.baudrate = rate

    def open(self):
        pass

    def write(self, fctArg1):
        pass


    def read(self):
        if not self.output:
            randFloat = float(randrange(-30000, 30000)) / 10000.0
            self.pm25 = float(max(10, randFloat + self.pm25))
            self.temp = randint(-1, 1) + self.temp
            self.output = self.timestamp + ' ' + self.reading3 + ' ' + self.reading4 + ' ' + str(self.pm25) + \
                      ' ' + str(self.temp)+ ' ' + str(self.humidity)+ ' ' + str(self.pressure) + '\r'

            # print('In read method:')
            # print(self.output)
        retChar = self.output[0]
        self.output = self.output[1:]
        return retChar



