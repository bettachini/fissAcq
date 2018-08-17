import visa

rm = visa.ResourceManager('@py')
print(rm.list_resources())

my_instrument = rm.open_resource('USB0::1689::868::C101891::0::INSTR')
print(my_instrument.query("*IDN?"))
