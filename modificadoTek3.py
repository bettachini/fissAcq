import os
import numpy as np
import time

class usbtmc:
    """Simple implementation of a USBTMC device driver, in the style of visa.h"""

    def __init__(self, device):
        self.device = device
        self.FILE = os.open(device, os.O_RDWR)

        # TODO: Test that the file opened

    def write(self, command):
        # os.write(self.FILE, command)
        os.write(self.FILE, command.encode('utf-8')) # turns str into bytes literal, a sequence of octets (ints 0 to 255)

    def read(self, length = 4000):
        return os.read(self.FILE, length)
        # return ((os.read(self.FILE, length)).decode()).rstrip('\n')

    def ask(self, command):
        self.write(command)
        return self.read()

    def getName(self):
        self.write("*IDN?")
        return self.read(300).decode().rstrip('\n')
        # return self.ask('*IDN?')

    def sendReset(self):
        self.write("*RST")


class TektronixScopeError(Exception):
    """Exception raised from the TektronixScope class

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, mesg):
        self.mesg = mesg
    def __repr__(self):
        return self.mesg
    def __str__(self):
        return self.mesg



class TekScope(usbtmc):
    """Class to control a Tek TDS2002B series oscilloscope"""
    def __init__(self, device='/dev/usbtmc0'):
        self.meas = usbtmc(device)
        self.name = self.meas.getName()
        # [self.dataCount, self.dataOffset] = self.ptsAcq()
        [self.dataCount, self.dataOffset] = [2500,6]
        print(self.name)


    def write(self, command):
        """Send an arbitrary command directly to the scope"""
        self.meas.write(command)

    def read(self, command):
        """Read an arbitrary amount of data directly from the scope"""
        return self.meas.read(command)

    def ask(self, command):
        """Write + Read"""
        return self.meas.ask(command)

    def textAsk(self, command):
        return (self.meas.ask(command) ).decode().rstrip('\n')

    def reset(self):
        """Reset the instrument"""
        self.meas.sendReset()

    def readBuff2(self):
        try:
            return self.ask('CURVE?')
        except TimeoutError:
            print('Probably requested channel has no data')
            raise

    def ptsAcq(self):	# ran once in order to obtain buffer parametres
        buff2 = self.readBuff2()	# read single buffer
        dataPointsCharacters= int(buff2[1:2])
        dataOffset= 2+ dataPointsCharacters
        return (int(buff2[2:2+ dataPointsCharacters])), dataOffset # number acquired points per buffer read, data bits offset in buffer

    def singleAcq(self,waitTime=1E-3):
        self.start_acq()
        while(self.is_busy()):
            time.sleep(waitTime)
        # return (np.frombuffer(readBuff2(test), dtype = np.dtype('int8').newbyteorder('<'), count= dataCount, offset= dataOffset) )  
        buff2 = self.readBuff2()	# reads single buffer 
        return ( np.frombuffer(buff2, dtype = np.dtype('int8').newbyteorder('<'), count= self.dataCount, offset= self.dataOffset) )	

    def ascii_read(self):
        """
        Reads channel waveform as ASCII but fails to read the whole 2500 available positions
        """
        self.set_data_encoding('ASCII')
        buff1 = self.ask('CURVE?')
        res1= np.asarray(buff1.split(','))
        # The output of CURVE? is scaled to the display of the scope
        self.offset = self.get_out_waveform_vertical_position()
        self.scale = self.get_out_waveform_vertical_scale_factor()
        # The following converts the data to the right scale
        Y = (res1 - self.offset)*self.scale
        return Y

    def bin_read(self):
        """
        Reads channel waveform as RIBinary
        """
        # self.set_data_encoding('RIBinary')
        try:
            buff2 = self.ask('CURVE?')
        except TimeoutError:
            print('Probably requested channel has no data')
            raise
        dataPointsCharacters= int(buff2[1:2])
        dataOffset= 2+ dataPointsCharacters
        dataCount= int(buff2[2:2+ dataPointsCharacters])
        res2 = np.frombuffer(buff2, dtype = np.dtype('int8').newbyteorder('<'), count= dataCount, offset= dataOffset)
        # The output of CURVE? is scaled to the display of the scope
        self.offset = self.get_out_waveform_vertical_position()
        self.scale = self.get_out_waveform_vertical_scale_factor()
        # The following converts the data to the right scale
        Y = (res2 - self.offset)*self.scale
        return Y

    def Xaxis(self):
        self.x_0 = self.get_out_waveform_horizontal_zero()
        self.data_start = self.get_data_start()
        self.data_stop = self.get_data_stop()
        self.delta_x = self.get_out_waveform_horizontal_sampling_interval()
        X_axis = self.x_0 + np.arange(self.data_start-1, self.data_stop)*self.delta_x
        return X_axis


##################################
## Method ordered by groups 
## borrowed from https://pypi.python.org/pypi/PyTektronixScope
###################################

#Acquisition Command Group 
    def start_acq(self):
        """Start acquisition"""
        self.write('ACQ:STATE RUN')
    def stop_acq(self):
        """Stop acquisition"""
        self.write('ACQ:STATE STOP')
    def single_pulse(self):
        self.write('ACQuire:STOPAfter SEQuence')


#Alias Command Group

#Bus Command Group

#Calibration and Diagnostic Command Group

#Cursor Command Group

#Data Logging Commands 

#Display Command Group

#Ethernet Command Group

#File System Command Group

#Hard Copy Command Group

#Horizontal Command Group

#Mark Command Group

#Math Command Group

#Measurement Command Group

#Miscellaneous Command Group
    def load_setup(self):
        l = self.textAsk('SET?')
        # l = (self.ask('SET?') ).decode().rstrip('\n')
        lok= [e.split(' ') for e in l.split(';')[1:]]
        if (len(lok[79])>2):  # line [79] can have 4 instead of 2 elements e.g. [':MATH:DEFINE', '"CH1', '-', 'CH2"']
            aux= lok[79][1]+ lok[79][2]+ lok[79][3]
            lok[79]= [lok[79][0], aux]
            # print(lok)
        dico = dict(lok)
        self.dico = dico

    def get_setup_dict(self, force_load=False):
        """Return the dictionnary of the setup 
        
        By default, the method does not load the setup from the instrument
        unless it has not been loaded before or force_load is set to true.
        """
        if not hasattr(self, 'dico') or force_load:
            self.load_setup()
        return self.dico

    def get_setup(self, name, force_load=False):
        """Return the setup named 'name' 
        
        By default, the method does not load the setup from the instrument
        unless it has not been loaded before or force_load is set to true.
        """
        if not hasattr(self, 'dico') or force_load:
            self.load_setup()
        return self.dico[name]

    def number_of_channel(self):
        """Return the number of available channel on the scope (4 or 2)"""
        if ':CH4:SCA' in self.get_setup_dict().keys():
            return 4
        else:
            return 2

#Save and Recall Command Group

#Search Command Group

#Status and Error Command Group
    def is_busy(self):
        ''' () -> boolean
        
        Returns False wheter oscilloscope finished an acquisition.
        
        >>> is_busy()
        False
        '''
        return int(self.ask('BUSY?'))==1


#Trigger Command Group

    def trigger_source(self, *arg):
        ''' () -> str
        Returns the trigger source { CH<x> | EXT | EXT5 | EXT10 }
        str ->
        Sets trigger source
        
        >>> trigger_source('CH1')
        trigger source set to CH1
        >>> trigger_source()
        CH1
        '''
        if (len(arg)==0):
            return self.textAsk('TRIGger:MAIn:PULse:SOUrce?')
        else:
            self.write('TRIGger:MAIn:PULse:SOUrce '+arg[0])
            # print ('trigger source set to ' +arg[0])

    def trigger_slope(self, *arg):
        ''' () -> string
        Returns FALL or RISE 
        string ->
        Sets trigger slope
        
        >>> trigger_slope(RISE)
        trigger slope set RISE
        >>> trigger_slope()
        RISE
        '''
        if (len(arg)==0):
            return float(self.ask('TRIGger:MAIn:EDGE:SLOpe?') )
        else:
            self.write('TRIGger:MAIn:EDGE:SLOpe '+ arg[0])

    def trigger_level(self, *arg):
        ''' () -> float
        Returns a float with the trigger level or if float given sets that trigger level to float value
        float ->
        Sets trigger level
        
        >>> trigger_level(1.2)
        trigger set to 1.20E+00 V
        >>> trigger_level()
        1.2
        '''
        if (len(arg)==0):
            return float(self.ask('TRIGger:MAIn:LEVel?') )
        else:
            self.write('TRIGger:MAIn:LEVel {:.2E}'.format(arg[0]))
            # print ('trigger set to {:.2E} V'.format(arg[0]))



#Vertical Command Group
    def channel_name(self, name):
        """Return and check the channel name
        
        Return the channel CHi from either a number i, or a string 'i', 'CHi'
        
        input : name is a number or a string
        Raise an error if the channel requested if not available 
        """
        n_max = self.number_of_channel()
        channel_list = ['CH%i'%(i+1) for i in range(n_max)]
        channel_listb = ['%i'%(i+1) for i in range(n_max)]
        if isinstance(name, int):
            if name > n_max:
                raise TektronixScopeError("Request channel %i while channel \
number should be between %i and %i"%(name, 1, n_max))
            return 'CH%i'%name
        elif name in channel_list:
            return name
        elif name in channel_listb:
            return 'CH'+name
        else:
            raise TektronixScopeError("Request channel %s while channel \
should be in %s"%(str(name), ' '.join(channel_list)))

    def is_channel_selected(self, channel):
        return int(self.ask('SELect:%s?'%(self.channel_name(channel))) )=='1'

    def get_channel_position(self, channel):
        return float(self.ask('%s:POS?'%self.channel_name(channel)))

    def get_channel_scale(self, channel):
        return float(self.ask('%s:SCA?'%self.channel_name(channel)))

    def get_out_waveform_vertical_scale_factor(self):
        return float(self.ask('%s:SCA?'%self.channel_name(channel)))

# Waveform Transfer Command Group
#    def data_source(self, *arg):
#        ''' () -> int$
#        Returns channel number of waveform to transfer at request
#        int ->$
#        Sets channel to transfer its waveform
#        $
#        >>> data_source(2)$
#        waveform to tranfer that of channel 2
#        >>> data_source()$
#        2
#        '''
#        if (len(arg)==0):
#            return int(self.textAsk('DATa:SOURce?' ) )
#        else:
#            name= 'CH%i'%(arg[0] )
#            # name= 'CH%i'%(str(arg[0] ))
#            # name = self.channel_name(str(arg[0] ) ) # name= 'CH#' string
#            self.write('DATa:SOURce '+ name )


    def set_data_source(self, name):
        ''' backwards compatibility use data_source function'''
        name = self.channel_name(name)
        self.write('DAT:SOUR '+str(name))

    def set_data_encoding(self, encoding='ASCII'):
        """Sets data transfer format [VAB]
        """
        self.write('DATa:ENCdg %s'%encoding)

    def set_data_start(self, data_start):
        """Set the first data points of the waveform record
        If data_start is None: data_start=1
        """
        if data_start is None:
            data_start = 1
        data_start = int(data_start)
        self.write('DATA:START %i'%data_start)

    def get_data_start(self):
        return int(self.ask('DATA:START?'))

    def horizontal_main_position(self, *arg):
        ''' () -> str
        Returns the horizontal centre position in seconds
        str ->
        Sets the horizontal centre position
        
        >>> horizontal_main_position(1E-3)
        horizontal centre position to 1 \mu s
        >>> horizontal_main_position()
        0.0E0
        '''
        if (len(arg)==0):
            return self.textAsk('HORizontal:MAIn:POSition?')
        else:
            self.write('HORizontal:MAIn:POSition '+ str(arg[0]) )


    def horizontal_main_scale(self, *arg):
        ''' () -> str
        Returns the horizontal scale
        str ->
        Sets the horizontal scale

        scale is in seconds per (main) division (with a total of 10 of them)
        
        >>> horizontal_main_scale(1E-3)
        horizontal scale to 1 \mu s
        >>> horizontal_main_scale()
        0.001
        '''
        if (len(arg)==0):
            return self.textAsk('HORizontal:MAIn:SCAle?')
        else:
            self.write('HORizontal:MAIn:SCAle '+ str(arg[0]) )

    def get_horizontal_record_length(self):
        return int(self.ask("horizontal:recordlength?"))

    def set_horizontal_record_length(self, val):
        self.write('HORizontal:RECOrdlength %s'%str(val))

    def set_data_stop(self, data_stop):
        """Set the last data points of the waveform record
        If data_stop is None: data_stop= horizontal record length
        """
        if data_stop is None:
            data_stop = self.get_horizontal_record_length()
        self.write('DATA:STOP %i'%data_stop)

    def get_data_stop(self):
        return int(self.ask('DATA:STOP?'))

    def get_out_waveform_horizontal_sampling_interval(self):
        return float(self.ask('WFMPre:XINcr?'))
        # return float(self.ask('WFMO:XIN?'))

    def get_out_waveform_horizontal_zero(self):
        return float(self.ask('WFMPre:XZERO?'))
        # return float(self.ask('WFMO:XZERO?'))

    def get_out_waveform_vertical_scale_factor(self):
        return float(self.ask('WFMPre:YMUlt?'))
        # return float(self.ask('WFMO:YMUlt?'))

    def get_out_waveform_vertical_position(self):
        return float(self.ask('WFMPre:YOFf?'))
        # return float(self.ask('WFMO:YOFf?'))

    def read_data_one_channel(self, channel=None, data_start=None,
                              data_stop=None, x_axis_out=False,
                              t0=None, DeltaT = None, booster=False):
        """Read waveform from the specified channel
        
        channel : name of the channel (i, 'i', 'chi'). If None, keep
            the previous channel
        data_start : position of the first point in the waveform
        data_stop : position of the last point in the waveform
        x_axis_out : if true, the function returns (X,Y)
                    if false, the function returns Y (default)
        t0 : initial position time in the waveform
        DeltaT : duration of the acquired waveform
            t0, DeltaT and data_start, data_stop are mutually exculsive 
        booster : if set to True, accelerate the acquisition by assuming
            that all the parameters are not change from the previous
            acquisition. If parameters were changed, then the output may
            be different than what is expected. The channel is the only
            parameter that is checked when booster is enable
        
        """
        # set booster to false if it the fist time the method is called
        # We could decide to automaticaly see if parameters of the method
        # are change to set booster to false. However, one cannot
        # detect if the setting of the scope are change
        # To be safe, booster is set to False by default.  
        if booster:
            if not hasattr(self, 'first_read'): booster=False
            else:
                if self.first_read: booster=False
        self.first_read=False
        if not booster:
            # Set data_start and data_stop according to parameters
            if (t0 != None or DeltaT != None):
                if data_stop is None and data_start is None:
                    x_0 = self.get_out_waveform_horizontal_zero()
                    delta_x = self.get_out_waveform_horizontal_sampling_interval()
                    data_start = int((t0 - x_0)/delta_x)+1
                    data_stop = int((t0+DeltaT - x_0)/delta_x)
                else: # data_stop is not None or data_start is not None 
                    raise TektronixScopeError("Error in read_data_one_channel,\
t0, DeltaT and data_start, data_stop args are mutually exculsive")
            if data_start is not None:
                self.set_data_start(data_start)
            if data_stop is not None:
                self.set_data_stop(data_stop)
            self.data_start = self.get_data_start()
            self.data_stop = self.get_data_stop()
        # Set the channel
        if channel is not None:
            self.set_data_source(channel)
        if not booster:
            if not self.is_channel_selected(channel):
                raise TektronixScopeError("Try to read channel %s which \
is not selectecd"%(str(name)))
        if not booster:
            self.write("DATA:ENCDG RIB")
            self.write("WFMO:BYTE_NR 2")
            self.offset = self.get_out_waveform_vertical_position()
            self.scale = self.get_out_waveform_vertical_scale_factor()
            self.x_0 = self.get_out_waveform_horizontal_zero()
            self.delta_x = self.get_out_waveform_horizontal_sampling_interval()

        X_axis = self.x_0 + np.arange(self.data_start-1, self.data_stop)*self.delta_x

        buffer = self.ask('CURVE?')
        res = np.frombuffer(buffer, dtype = np.dtype('int16').newbyteorder('>'),
                            offset=int(buffer[1])+2)
        # The output of CURVE? is scaled to the display of the scope
        # The following converts the data to the right scale
        Y = (res - self.offset)*self.scale
        if x_axis_out:
            return X_axis, Y
        else:
            return Y

#Zoom Command Group

