 # import the library
import can
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

# iterate over received messages
for msg in bus:
    print(f"{msg.arbitration_id:X}: {msg.data}")


# or use an asynchronous notifier
#notifier = can.Notifier(bus, [can.Logger("recorded.log"), can.Printer()])