#! /usr/bin/python
# coding=utf-8

# import tek
import os

class usbtmc:
    """Simple implementation of a USBTMC device driver, in the style of visa.h"""

    def __init__(self, device):
        self.device = device
        self.FILE = os.open(device, os.O_RDWR)

        # TODO: Test that the file opened

    def write(self, command):
        os.write(self.FILE, command);

    def read(self, length = 4000):
        return os.read(self.FILE, length)

    def getName(self):
        self.write("*IDN?")
        return self.read(300)

    def sendReset(self):
        self.write("*RST")

#
#class TektronixTDSseries:
#    """Class to control a Tek TDS2000 series oscilloscope"""
#    def __init__(self, device):
#        self.meas = usbtmc(device)
#
#        self.name = self.meas.getName()
#
#        print self.name
#
#    def write(self, command):
#        """Send an arbitrary command directly to the scope"""
#        self.meas.write(command)
#
#    def read(self, command):
#        """Read an arbitrary amount of data directly from the scope"""
#        return self.meas.read(command)
#
#    def reset(self):
#        """Reset the instrument"""
#        self.meas.sendReset()
#


# Initialize our scope Tektronix TDS2002B
Tek = usbtmc("/dev/usbtmc0")
# Tek = tek.TektronixTDSseries("/dev/usbtmc0")

# Asks for IDN
Tek.write('*IDN?')
print(Tek.read(100))

# Asks for measurement parameters
Tek.write('MEASUREMENT?')
print(Tek.read(400))

# Asks for acquisition parameters
Tek.write('ACQUIRE?')
print(Tek.read(400))

# Stablishes Channel 1 as data source
Tek.write('DATA:SOURCE CH1')

# Queries curve data format 
# default: SRIBINARY
# 2-71: signed integer data-point, -32768 to 32767 when DATa:WIDth is 2, 
# The upper limit is one division above the top of the screen and the lower limit is one division below the bottom of the screen.
# least significant byte is transferred first
Tek.write('DATa:ENCdg?')
print(Tek.read(400))

# Stops acquisition
Tek.write('ACQuire:STATE STOP')


