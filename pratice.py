import numpy as np
import matplotlib
from matplotlib.widgets import Button
import matplotlib.pyplot as plt
import can
from can import Message
#import time

# arguments: datastring = bytestring, input_array --> to join upper and lower byte = [[upperbyte, lowerbyte, multiplier],...]
# contd. to use byte without addition [[byte, multiplier],...]

path = "PCAN-Basic API\input file.txt"
file = open(path)
text_file = file.read()
list_file = text_file.splitlines()

## initialising bus object
interface = "pcan"
channel = "PCAN_USBBUS1"
state1 = can.bus.BusState.PASSIVE
bitrate = 500000
using_bus = False
state = 0

try:
    bus = can.Bus(interface=interface,
                channel=channel,
                receive_own_messages=True)
    using_bus = True
except:

    bus = list_file
    using_bus = False

print(using_bus)

def bytearray_to_list_general(data_string, input_array):
    try:    
        data_string = bytestring[bytestring.index("b'")+2:-2]
    except: 
        data_string = bytestring[bytestring.index('b"')+2:-2]
    data_string = data_string.encode('ASCII').decode("unicode_escape")
    output_list = []
    for values in input_array:
        if len(values) == 3:
            output_list.append(int(str(hex(ord(data_string[values[0]]))) + str(hex(ord(data_string[values[1]])))[2:], base=16)*values[-1])
        else:
            output_list.append(ord(data_string[values[0]])-1)


    return output_list

def colorheatmap(color,value, min_max, lim):
    if value < min_max[0] or value > min_max[1]:
        return  [1,0,0]
    elif color == "red":
        return [1,1-value/lim,0]
    elif color == "green":
        return [0.4,1-value/lim,0]

def showError(ifError):
    if ifError == True:
        start_message_button.color, start_message_button.hovercolor = "red", "red"
        stop_message_button.color, stop_message_button.hovercolor = "red", "red"
        reset_message_button.color, reset_message_button.hovercolor = "green", "green"
    elif ifError == False:
        start_message_button.color, start_message_button.hovercolor = "lightgray", "white"
        stop_message_button.color, stop_message_button.hovercolor = "lightgray", "white"
        reset_message_button.color, reset_message_button.hovercolor = "lightgray", "white"

#button message functions
# Normal current 0x0037 5.5A
# Lower current 0x000A 1A
# Charger Voltage 0x1170 600
# Slow Charge Threshhold 32700 3.27V
# Stop Charge 41500 4.15V
# Charge Out ID 405

def start_message(buttonpos):
    
    if state == 2:
        return
    msg= Message(arbitration_id=403105268, data=[18,102,0,10,1,0])
    try:
        bus.send(msg=msg,timeout=None)
    except:
        print("unable to send message")

def stop_message(buttonpos):
    if state == 2:
        return
    msg= Message(data=[0,0,0,0,0,0])
    try:
        bus.send(msg=msg,timeout=None)
    except:
        print("unable to send message")

def reset_message(buttonpos):
    if state == 2:
        return
    elif state == 0 or state == 1:
        showError(False)
        pass

    


loops_between_updates = 1
number_of_colums, number_of_rows, number_of_cells = 24, 6, 144
voltage_lim, temperature_lim = 20, 40 #if voltage exceeds this number it would cause the program to crash
code_for_val, code_for_vinf, code_for_tinf, code_for_stat = "400", "402", "403", "401"
max_temp, max_volt = 0, 0
iter_total = 0



#figure and axis initialization
final_array = np.empty(shape=(number_of_colums,number_of_rows))
final_array2 = np.empty(shape=(number_of_colums,number_of_rows))
fig, (ax,ax2,ax3) = plt.subplots(1,3, height_ratios = [1], width_ratios = [3,3,1])
fig.set_size_inches(8,8)
fig.tight_layout()
axes_list = [ax,ax2,ax3]

ax.set_title("Voltage")
ax2.set_title("Temperature")
ax3.set_title("Info")

ax.axis('on')
ax2.axis('on')
ax3.axis('off')


ax.set_xlim((-1,6))
ax.set_ylim((-1,24))

ax2.set_xlim((-1,6))
ax2.set_ylim((-1,24))

ax3.set_xlim((0,4))
ax3.set_ylim((0,12))


# im = ax.imshow(np.zeros(shape=(12,12)), cmap="magma_r")
# im2 = ax2.imshow(np.zeros(shape=(12,12)), cmap="magma_r")


#buttons
button1_ax = plt.axes([0.8,0.25,0.1,0.1])
button2_ax = plt.axes([0.8,0.15,0.1,0.1])
button3_ax = plt.axes([0.8,0.05,0.1,0.1])

start_message_button = Button(button1_ax, "start")
stop_message_button = Button(button2_ax, "stop")
reset_message_button = Button(button3_ax, "reset \n charge")

start_message_button.on_clicked(start_message)
stop_message_button.on_clicked(stop_message)
reset_message_button.on_clicked(reset_message)

plt.show(block=False)
# tstart = time.time()





for bytestring in bus:
    if using_bus == True:
        bytestring = f"{bytestring.arbitration_id:X}: {bytestring.data}"
    else:
        pass
    iter_total += 1
    if bytestring.startswith(code_for_val) == True:     #for CELLVAL

        cell_array = bytearray_to_list_general(bytestring, [[0,1],[2,3,10**-4],[4,5,1]])
    elif bytestring.startswith(code_for_vinf) == True:  #for BMSVINF 
        volt_info_list = bytearray_to_list_general(bytestring, [[2,1],[5,1],[0,1,10**-4],[3,4,10**-4],[6,7,10**-4]])

        ax3.text(x=-2, y=10, s=f'V_max = {round(volt_info_list[2],3)} @ Cell {volt_info_list[0]}', fontsize="small")
        ax3.text(x=-2, y=9, s=f'V_min = {round(volt_info_list[3],3)} @ Cell {volt_info_list[1]}', fontsize="small")
        ax3.text(x=-2, y=8, s=f'V_avg = {round(volt_info_list[4],3)}',fontsize="small")

        continue
    elif bytestring.startswith(code_for_tinf) == True:  #for BMSTINF
        temp_info_list = bytearray_to_list_general(bytestring, [[2,1],[5,1],[0,1,1],[3,4,1],[6,7,1]])

        ax3.text(x=-2, y=7, s=f'T_max = {round(temp_info_list[2],3)} @ Cell {temp_info_list[0]}', fontsize="small")
        ax3.text(x=-2, y=6, s=f'T_min = {round(temp_info_list[3],3)} @ Cell {temp_info_list[1]}', fontsize="small")
        ax3.text(x=-2, y=5, s=f'T_avg = {round(temp_info_list[4],3)/3}',fontsize="small")
        continue
    elif bytestring.startswith(code_for_stat) == True:  #for BMSSTAT
        state_info = bytearray_to_list_general(bytestring, [[0,1],[1,1],[2,1],[3,1],[4,1],[5,1]])
        state_info = [x+1 for x in state_info]
        ax3.text(-2, y=4, s=f"No Errors")
        if 1 in state_info:
            state = 2
            showError(True)
        continue
    else:
        continue
    
    # converts list of 144 cells to columns and rows
    column = 0
    while cell_array[0] >= number_of_rows:
        cell_array[0] -=  number_of_rows
        column += 1
        
    
    # to prevent possible indexing error (optional)
    try:
        final_array[column][cell_array[0]] = cell_array[1]
        final_array2[column][cell_array[0]] = cell_array[2]
        
    except:
        print(f'column:{column}, row:{cell_array[0]}')
    
    # annotated text and colour formats: rounds float values to two decimal places, 
    # ax.text adds the text value for each cell at their column and row in the table
    # background colour for text varies with voltage/temperature to create heatmap
    ann = ax.text(

        x=cell_array[0],y=column,s=str(round(cell_array[1],3)), fontsize = 'x-small',
         horizontalalignment = "center", backgroundcolor=matplotlib.colors.to_hex(colorheatmap("green",cell_array[1],[2,5],20)), color = "black"
       
         )
    ann2 = ax2.text(

        x=cell_array[0],y=column,s=str(round(cell_array[2],3)), fontsize = 'x-small',
         horizontalalignment = "center", backgroundcolor=matplotlib.colors.to_hex(colorheatmap("red",cell_array[2],[5,30],50)), color = "black"
       
         )

    # how many iteration between each chart update
    if loops_between_updates%144 == 0:
        fig.canvas.draw()

        # refresh rate
        plt.pause(0.1)

        # clears frame after each interation

        for axes_iter in axes_list:
            for index,child in enumerate(axes_iter.get_children()):
                #prevents error applying to "artist" object
                if isinstance(child, matplotlib.text.Text) and isinstance(child.get_position()[0], int): #prevents error caused by trying to apply function to matplotlib.axes object
                    child.remove()   
     
        
    loops_between_updates += 1

#to check frame_rate    
'''
total_time = time.time() - tstart
print(f"In time {total_time}, made {iter_total} iterations for fps {iter_total/(total_time)}")
file.close()

'''