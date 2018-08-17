#! /usr/bin/python
# coding=utf-8

import tek

# Initialize our scope
test = tek.TekScope("/dev/usbtmc0")

# Asks for IDN
test.write('*IDN?')
print(test.read(100))

# Asks for measurement parameters
test.write('MEASUREMENT?')
print(test.read(400))

# Asks for acquisition parameters
test.write('ACQUIRE?')
print(test.read(400))

# Stablishes Channel 1 as data source
test.write('DATA:SOURCE CH1')

# Queries curve data format 
# default: SRIBINARY
# 2-71: signed integer data-point, -32768 to 32767 when DATa:WIDth is 2, 
# The upper limit is one division above the top of the screen and the lower limit is one division below the bottom of the screen.
# least significant byte is transferred first
test.write('DATa:ENCdg?')
print(test.read(400))

# Stops acquisition
# test.write('ACQuire:STATE STOP')

# starts acquisition
test.start_acq()

