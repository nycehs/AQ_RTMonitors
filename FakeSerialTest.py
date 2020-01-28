import FakeSerial as serial

def main():
    ser = serial.Serial('device', 19200)
    ser.open()
    # ser.write(bytes('sd on\r'))
    for i in range(200):
        rdg = ""
        ch = ser.read()
        
        while ch.decode('utf-8', errors='ignore') != '\r':
            rdg = rdg + ch.decode('utf-8', errors='ignore')
            ch = ser.read()
            
        print('i=', i, rdg)

if __name__ == "__main__":
    main()    
