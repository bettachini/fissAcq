# usbtmc to communicate 
# from http://www.cibomahto.com/2010/04/controlling-a-rigol-oscilloscope-using-linux-and-python/

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
 
	def ask(self, command):
		self.write(command)
		return self.read()

    def getName(self):
        self.write("*IDN?")
        return self.read(300)
 
    def sendReset(self):
        self.write("*RST")


class TektronixScope(usbtmc):
	'''

	Heavily based on https://pypi.python.org/pypi/PyTektronixScope
	'''
	def __init__(self, device):
		super(TektronixScope, self).__init__(device)
	
###################################
## Method ordered by groups 
###################################

#Acquisition Command Group 
# 	def start_acq(self):
# 		"""Start acquisition"""
#         self.write('ACQuire:STATE RUN')

#	def stop_acq(self):
#		"""Stop acquisition"""
#		self.write('ACQuire:STATE STOP')
