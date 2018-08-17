#! /usr/bin/python
# coding=utf-8

import visa

rm = visa.ResourceManager('@py')

# abre la sesión de comunicacion con el TDS 2002B
tek = rm.open_resource('USB0::1689::868::C101891::0::INSTR')

#

# cierra la sesión
rm.close
