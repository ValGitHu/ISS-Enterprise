import threading
import serial

connected = False
port = '/dev/ttyUSB0'
baud = 4800

serial_port = serial.Serial(port, baud, timeout=0)

def handle_data(data):
    print(data)

def read_from_port(ser):
    global connected
    while not connected:
        #serin = ser.read()
        connected = True

        while True:
           print("test")
           reading = ser.readline().decode()
           handle_data(reading)

thread = threading.Thread(target=read_from_port, args=(serial_port,))
thread.start()
