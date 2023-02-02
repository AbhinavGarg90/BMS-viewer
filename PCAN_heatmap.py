# import the library
import can
import numpy as np
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import time
import math


## initialising bus object
interface = "pcan"
channel = "PCAN_USBBUS1"
state = can.bus.BusState.PASSIVE
bitrate = 500000

# create a bus instance
# many other interfaces are supported as well (see documentation)
bus = can.Bus(interface=interface,
              channel=channel,
              receive_own_messages=True)

'''
# send a message
message = can.Message(arbitration_id=123, is_extended_id=True,
                      data=[0x11, 0x22, 0x33])
bus.send(message, timeout=0.2)
'''

## initialising heatmap
fig = plt.figure()
ax = fig.add_subplot(111)
im = ax.imshow(np.zeros(shape=(12,12)), cmap="magma_r")
plt.show(block=False)

final_array = np.empty(shape=(12,12))
loops_between_updates = 1


## iterate over received messages
for msg in bus:
    x = f"{msg.arbitration_id:X}: {msg.data}"
    if x.startswith("400") == True:     #filters out non 400 inputs
        pass
    else:
        continue
    
    # handling error for input coming as b" instead of b'
    try:    
        data_string = x[x.index("b'")+2:-2]
    except: 
        data_string = x[x.index('b"')+2:-2]
    data_string = data_string.encode('ASCII').decode("unicode_escape")
    
    #converts input from hex to float
    output_list = []
    output_list.append(ord(data_string[0])-1)
    output_list.append(int(str(hex(ord(data_string[2]))) + str(hex(ord(data_string[3])))[2:], base=16)*10**-4)
    output_list.append(int(str(hex(ord(data_string[4]))) + str(hex(ord(data_string[5])))[2:], base=16))
    
    # converts list of 144 cells to columns and rows
    column = 0
    while output_list[0] > 11:
        output_list[0] -= 12
        column += 1
    
    # to prevent possible indexing error
    try:
        final_array[column][output_list[0]] = output_list[1]
    except:
        print(f'column:{column}, row:{output_list[0]}')
    
    # annotated text and colour formats: rounds float values to two decimal places, 
    # 20 is used as max value for normalisation, larger than 20 may cause errors
    ann = ax.text(

        x=output_list[0],y=column,s=str(round(output_list[1],2)), fontsize = 'x-small',
         horizontalalignment = "center", backgroundcolor=matplotlib.colors.to_hex([1,1-output_list[1]/20,0]), color = "black", wrap = True
       
         )
    
    # how many iteration between each chart update
    if loops_between_updates%144 == 0:
        im.set_array(final_array) 
        fig.canvas.draw()

        # refresh rate
        plt.pause(0.1)

        # clears numericals from frame after each interation
        for index,child in enumerate(ax.get_children()):
            if isinstance(child, matplotlib.text.Text): #prevents error caused by trying to apply function to matplotlib.axes object
                if isinstance(child.get_position()[0], int): #prevents error applying to "artist" object
                    child.remove()
     
        
    loops_between_updates += 1
