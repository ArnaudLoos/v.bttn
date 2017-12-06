from bluepy.btle import *
import time
import struct
import threading


# ############################################################################
#                                 CLASSES
# ############################################################################
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

#    def handleDiscovery(self, dev, isNewDev, isNewData):
#        if isNewDev:
#            print "Discovered device", dev.addr
#        elif isNewData:
#            print "Received new data from", dev.addr

    def handleNotification(self, cHandle, data):
        val_data = struct.unpack("B"*len(data),data)
        #val_data is a tuple
        if val_data[0] == 1:
            print "Button press"
        elif val_data[0] == 0:
            print "Button release"
        elif val_data[0] == 3:
            print "Long button press"
        elif val_data[0] == 4:
            print "fall detected"

# ############################################################################
#                             CLASSES END
# ############################################################################


# ############################################################################
#                             CONFIGURATION
# ############################################################################

# - variables to be initialized once -
myVbttn = None
scanner = Scanner().withDelegate(ScanDelegate())

# - CONSTANTS -
NOTIFICATION_ON     = b"\x01\x00"
# NOTIFICATION_OFF  = b"\x01\x00"
SCAN_TIME           = 2.0
VERIFICATION_TOKEN  = bytearray([0x80, 0xBE, 0xF5, 0xAC, 0xFF])
UUID_VERIFICATION   = "FFFFFFF5-00F7-4000-B000-000000000000"
UUID_BUTTON_ENABLE  = "FFFFFFF2-00F7-4000-B000-000000000000"
UUID_NOTIFICATION   = "fffffff4-00f7-4000-b000-000000000000"

# TODO: Gather all hard-coded "magic numbers" here

# ############################################################################
#                           CONFIGURATION END
# ############################################################################


# Run the scan and return any devices found
def run_scan():
    return scanner.scan(SCAN_TIME)


# ########
#  TEST
# ########
counter = 0
while counter < 100:
    devices = run_scan()
    for dev in devices:
        for (adtype, desc, value) in dev.getScanData():
            if (desc == "Complete Local Name") and (value[:6] == "V.ALRT") :
                print "Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi)
    counter += 1
exit()
###########



# Run the scan
devices = run_scan()

for dev in devices:
    print "Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi)
    for (adtype, desc, value) in dev.getScanData():
#        print "  %s = %s" % (desc, value)
        if (desc == "Complete Local Name") and (value[:6] == "V.ALRT") :
            myVbttn = dev
#            print "[Device %s found as %s]" % (myVbttn.addr, value)
            print "\nDevice %s is a v.bttn\n" % (myVbttn.addr)

if myVbttn is not None:
    print("Connecting to vBttn...")
    try:
        p = Peripheral(myVbttn.addr,myVbttn.addrType).withDelegate(ScanDelegate())
    except:
        print("Error Occured!")
    print "\tConnected to ", myVbttn.addr

# Read battery level
    item = p.getCharacteristics()
    for k in item:
        if k.uuid==AssignedNumbers.batteryLevel:
            bat_char = k
        elif k.uuid == AssignedNumbers.txPowerLevel:
            tx_char = k
    bat_data = bat_char.read()
    #tx data is a signed 8 bit integer
    tx_data = tx_char.read()
#    print tx_data.type()
    bat_data_value = ord(bat_data[0])
#    tx_data_value = ord(tx_data[0])
#    tx_data_value = struct.unpack('b', tx_data[0])
    print "\tBattery: ", bat_data_value, "%"
#    print "\tTX: ", tx_data_value, "-dBM"

    print("Sending verification token...")
    ch = p.getCharacteristics(uuid=UUID_VERIFICATION)[0]
    ch.write(VERIFICATION_TOKEN)
    print("\tVerified")

    print("Enabling button press...")
    ch = p.getCharacteristics(uuid=UUID_BUTTON_ENABLE)[0]
#    print("ch was: ", ch.read())
    ch.write(bytearray([0x07]))
#    print("ch is: ", ch.read())
    print("\tEnabled")

    print("Enabling notifications...")
    char = p.getCharacteristics(uuid=UUID_NOTIFICATION)[0]
    ccc_desc = char.getDescriptors(forUUID=0x2902)[0]
#    print("notif was: ", ccc_desc.read())
    ccc_desc.write(NOTIFICATION_ON, withResponse=True)
#    print("notif is: ", ccc_desc.read())
    print("\tDone")
else:
    print("myVbttn reporting as None")

while True:
    if p.waitForNotifications(1.0):
        # handleNotification() was called
        #raise BTLEException(BTLEException.DISCONNECTED, "Device disconnected")
        #bluepy.btle.BTLEException: Device disconnected
        continue
    print("Waiting...")

#finally:
#    p.disconnect();

