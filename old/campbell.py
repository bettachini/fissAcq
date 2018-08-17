def eins(channel):
    ''' 
    Returns single channel as horizontal array 
    '''
    test.set_data_source(channel)
    Y= test.bin_read()
    return Y

def zwei():
    '''
    Returns both channels as horizontal array
    '''
    Y1= eins(1)
    Y2= eins(2)
    Meas2= np.vstack([Y1, Y2])
    return Meas2

def single():
    '''
    Queries both channels, restarts acquistion
    '''
    Meas2= zwei()
    test.start_acq()
    return Meas2

def emitZeit(Meas2):
    T= tek3.TekScope.Xaxis(test)
    
    plt.grid()
    plt.xlabel('tiempo [s]')
    plt.ylabel('dif. potencial [v]')
    plt.plot(T, Meas2[0,:])

def vertMitZeit(Meas2):
    T= tek3.TekScope.Xaxis(test)
        
    fig, (ax0, ax1) = plt.subplots(nrows=2, sharex=True)
    fig.set_size_inches(8,8)
    fig.subplots_adjust(hspace=0.000)

    ax0.plot(T, Meas2[0,:], 'y')
    # Make the y-axis label and tick labels match the line color.
    ax0.set_ylabel('ch 1 [V]', color='y')
    ax0.grid(True)

    ax1.plot(T, Meas2[1,:], 'c')
    ax1.set_ylabel('ch 2 [V]', color='c')
    ax1.set_xlabel('tiempo [s]')
    ax1.grid(True)
    
    plt.show()


