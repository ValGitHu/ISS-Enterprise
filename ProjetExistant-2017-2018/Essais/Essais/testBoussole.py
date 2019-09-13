from qmc5883l import *

mag_sens = QMC5883L()

while True:
    [x, y, z] = mag_sens.get_magnet()
    print(mag_sens.get_magnet())
    angle=((atan2(x,y)/pi)*180)+180

    print("angle=",angle)
    
    time.sleep(1)
