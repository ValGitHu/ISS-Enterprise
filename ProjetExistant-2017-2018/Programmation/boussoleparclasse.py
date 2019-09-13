"""import qmc5883l

mag_sens = qmc5883l.QMC5883L()

[x, y, z] = mag_sens.get_magnet()

print("{}".format(x))
print("x=", x)
print("y=", y)
print("z=", z)
print(mag_sens.get_magnet())
"""
# -*- coding: utf-8 -*-
from smbus2 import SMBus
import time
from math import atan2
pi=3.14159265359
"""Driver for the QMC5883l 3-Axis Magnetic Sensor
Datasheet: https://github.com/e-Gizmo/QMC5883L-GY-271-Compass-module/blob/master/QMC5883L%20Datasheet%201.0%20.pdf # noqa
"""

__author__ = "Fabian Mruck"
__email__ = "github@ffabi.com"
__license__ = 'MIT'
__version__ = 'v0.1'

"""HISTORY
v.01 - First
"""
RATES = {
    10: 0,
    50: 1,
    100: 2,
    200: 3,
}

OSR = {
    64: 3,
    128: 2,
    256: 1,
    512: 0,
}

REG_OUT_X_LSB = 0x00
REG_OUT_X_MSB = 0x01
REG_OUT_Y_LSB = 0x02
REG_OUT_Y_MSB = 0x03
REG_OUT_Z_LSB = 0x04
REG_OUT_Z_MSB = 0x05
REG_STATUS = 0x06
REG_TEMP_LSB = 0x07
REG_TEMP_MSB = 0x08
REG_CONF_1 = 0x09
REG_CONF_2 = 0x0a
REG_RST_PERIOD = 0x0b
REG_CHIP_ID = 0x0d
TEMP_CORR = 47  # Just a first value


class QMC5883L(object):
    '''Driver for the QMC5883l 3-Axis Magnetic Sensor'''
    def __init__(self,
                 adress=13,
                 busnum=1,
                 cont_mode=True,
                 rate=10,
                 full_scale=True,
                 over_sampling_rate=256,
                 interupt=True,
                 pointer_roll=False,
                 restore=False
                 ):
        """
        TODO: explain allwed values in ValueError
        """
        if over_sampling_rate in OSR:
            self.over_sampling_rate = OSR.get(over_sampling_rate)
        else:
            raise ValueError('oversampling rate is not a allwed value')
        if rate in RATES:
            self.rate = RATES.get(rate)
        else:
            raise ValueError('rate is not a allowed value')

        self.bus = SMBus(busnum)
        self.adress = adress
        self.full_scale = full_scale
        self.interupt = interupt
        self.pointer_roll = pointer_roll
        self.restore = restore
        self.cont_mode = cont_mode

        """
        TODO: Maybe a warning is better than print
        """
        if self.bus.read_byte_data(self.adress, REG_CHIP_ID) != 0xff:
            print("Wrong Chip ID, are you shure this is the correct Chip?")
        self.set_config()

    def set_config(self):
        if self.cont_mode:
            self.cntrl_reg1 = 1
        if self.full_scale:
            self.cntrl_reg1 = self.cntrl_reg1 + 1 * (2**2)
        self.cntrl_reg1 = self.cntrl_reg1 + self.over_sampling_rate * (2**4)
        self.cntrl_reg1 = self.cntrl_reg1 + self.rate * (2**6)
        self.cntrl_reg2 = self.interupt
        self.cntrl_reg2 = self.cntrl_reg2 + self.pointer_roll * (2 ** 6)
        self.cntrl_reg2 = self.cntrl_reg2 + self.restore * (2 ** 7)
        self.bus.write_byte_data(self.adress, REG_CONF_1, self.cntrl_reg1)
        self.bus.write_byte_data(self.adress, REG_CONF_2, self.cntrl_reg2)


    def _convert_data(self, data, offset):
        if self.full_scale:
            max_mag = 8
        else:
            max_mag = 2
        magval = ((data[offset + 1] << 8) + data[offset])
        
        if magval > (2 ** 15) - 1:
            magval = magval - (2 ** 16)

        return magval

    def get_magnet(self):
        data = self.bus.read_i2c_block_data(self.adress, REG_OUT_X_LSB, 6)
        x = self._convert_data(data, REG_OUT_X_LSB)
        y = self._convert_data(data, REG_OUT_Y_LSB)
        z = self._convert_data(data, REG_OUT_Z_LSB)
        return [x, y, z]

mag_sens = QMC5883L()

while True:
    [x, y, z] = mag_sens.get_magnet()
    print(mag_sens.get_magnet())
    angle=((atan2(x,y)/pi)*180)+180

    print("angle=",angle)
    
    time.sleep(1)