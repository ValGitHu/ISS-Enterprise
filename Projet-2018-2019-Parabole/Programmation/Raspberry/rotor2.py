import serial
import time

ser = serial.Serial('/dev/ttyUSB0')
print(ser.name)
#ser.write(b'sPRO0000\r\n')
time.sleep(1)
#ser.write(b'sCAL0000\r\n')
#time.sleep(1)
#ser.write(b'sCAR0360\r\n')
#time.sleep(1)
ser.write(b'W090 000\r\n')
time.sleep(2)
ser.close()
      
