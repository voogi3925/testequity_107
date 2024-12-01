

import math
import numpy as np 
import time
import re
import sys

from pushbullet import Pushbullet
from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder



######################################################################################
######################################################################################
# functions for pushbullet notification
######################################################################################
######################################################################################


def send_pushbullet_notification(message: str):
    access_token = "your_access_token"  # Pushbullet 설정에서 얻은 Access Token
    pb = Pushbullet(access_token)
    push = pb.push_note("Python Notification", message)
    if push:
        print("알림이 성공적으로 전송되었습니다.")
    else:
        print("알림 전송에 실패하였습니다.")

######################################################################################
######################################################################################
# functions for testequity model 107
######################################################################################
######################################################################################

def read_float(addr):  # read 32 bit float
    result = client.read_input_registers(int(addr), 2)
    assert (not result.isError())
    return BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG,
                                              wordorder=Endian.BIG).decode_32bit_float()


def write_float(addr, value):  # write 32 bit float
    builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
    builder.add_32bit_float(float(value))
    rq = client.write_registers(int(addr), builder.build(), skip_encode=True)
    assert (not rq.isError())
    return


def read_uint(addr):  # read 16 bit unsigned integer
    result = client.read_input_registers(int(addr), 1)
    assert (not result.isError())
    return result.registers[0]
    # return int(result.registers[0])


def write_uint(addr, value):  # write 16 bit unsigned integer
    rq = client.write_registers(int(addr), int(value))
    assert (not rq.isError())
    return

def read_int(addr):  # read 16 bit signed integer
  result = client.read_input_registers(int(addr), 1)
  assert (not result.isError())
  d = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)  # need to do this as it might be a negative value
  return d.decode_16bit_int()


def write_int(addr, value):  # write 16 bit signed integer
  value = int(value)   
  if (value < 0):  # need to convert negative values to two's complement
    builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)    
    builder.add_16bit_int(value)
    payload = builder.to_registers() 
    rq = client.write_registers(int(addr), payload)
  else:  
    rq = client.write_registers(int(addr), value)
  assert (not rq.isError())
  return


def read_long_int(addr):  # read 32 bit integer
    result = client.read_input_registers(int(addr), 2)
    assert (not result.isError())
    return BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG,
                                              wordorder=Endian.BIG).decode_32bit_int()


def read_string(addr, numchars):  # read string.  need to know number of characters, typically 15 or 20 for F4T
    result = client.read_input_registers(int(addr), int(numchars))
    assert (not result.isError())
    # print (result.registers)
    output = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG,
                                                wordorder=Endian.BIG).decode_string(int(numchars) * 2)
    return re.sub(u'([\u0000])', "", output.decode(sys.getdefaultencoding()))


def set_word_order():
    word_order = read_int(6736)
    if word_order == 1331:  # word_order = 1331 is Low High, 1330 is High Low
        print("Word Order = ", word_order)
        write_int(6736, 1330)
        print("Changed Word Order to High Low")


def temp_chamber_check():
    print("####################")
    print("checking chamber...")
    #client = ModbusTcpClient(address_chamber, port=502)
    if client.connect():
        print("Connected to Modbus server successfully")
    else:
        print("Failed to connect to Modbus server")
    
    set_word_order()  # make sure word order is set to High Low
    
    print("F4T Device Name =", read_string(46, 20))  # TestEquity Model #, 20 byte string
    print("F4T Part Number =", read_string(16, 15))  # F4T part #, 15 byte string
    print("F4T Serial Number = ", read_long_int(12))
    
    part_num=read_int(27)  # 49, 50, 55 or 56 for TestEquity chambers
    print(f"part_num: {part_num}")
    IsCascade = False
    IsHumid = False
    
    units = read_int(1328)  # read global units, 15=C, 30=F.  This is value displayed on F4T screen
    if units==15:
        print("Global unit is 'C")
    else:
        print("Global unit is 'F")
    write_int(6730, units) # change modbus-tcp units to be same value
    
    if IsCascade:
      set_addr = 4042
    else:
      set_addr = 2782  
    
    # write_int(16594,63)  # turn power on, same as pressing Power button on F4T front screen.  Switch must be in EVENT1 position for this to work.
    
    print("Chamber Air Temp = %.1f" % (read_float(27586)))
    if IsCascade:
      print("Part Temp = %.1f" % (read_float(29346)))
    
    print("Current Temperature Set Point = %.1f" % read_float(set_addr))
    
    time.sleep(2)  # small delay just for this demo code
    # write_int(16594, 62)  # turn power off, same as pressing Power button on F4T front screen.  Switch must be in EVENT1 position for this to work.
    # time.sleep(2)  # small delay just for this demo code
    print("checking chamber ends")
    client.close()


def temp_chamber_power_on():
    print("####################")
    print("turn on chamber...")
    client = ModbusTcpClient(address_chamber, port=502)
    if client.connect():
        print("Connected to Modbus server successfully")
    else:
        print("Failed to connect to Modbus server")
    
    units = read_int(1328)  # read global units, 15=C, 30=F.  This is value displayed on F4T screen
    if units==15:
        print("Global unit is 'C")
    else:
        print("Global unit is 'F")
    set_addr = 2782  
    
    write_int(16594,63)  # turn power on, same as pressing Power button on F4T front screen.  Switch must be in EVENT1 position for this to work.
    
    print("Chamber Air Temp = %.1f" % (read_float(27586)))
    if IsCascade:
      print("Part Temp = %.1f" % (read_float(29346)))
    
    print("Current Temperature Set Point = %.1f" % read_float(set_addr))
    
    time.sleep(2)  # small delay just for this demo code
    # write_int(16594, 62)  # turn power off, same as pressing Power button on F4T front screen.  Switch must be in EVENT1 position for this to work.
    # time.sleep(2)  # small delay just for this demo code
    print("turn on ends")
    client.close()

def temp_chamber_power_off():
    print("####################")
    print("turn off chamber...")
    client = ModbusTcpClient(address_chamber, port=502)
    if client.connect():
        print("Connected to Modbus server successfully")
    else:
        print("Failed to connect to Modbus server")
    
    units = read_int(1328)  # read global units, 15=C, 30=F.  This is value displayed on F4T screen
    if units==15:
        print("Global unit is 'C")
    else:
        print("Global unit is 'F")
    set_addr = 2782  
    
    #write_int(16594,63)  # turn power on, same as pressing Power button on F4T front screen.  Switch must be in EVENT1 position for this to work.
    
    print("Chamber Air Temp = %.1f" % (read_float(27586)))
    if IsCascade:
      print("Part Temp = %.1f" % (read_float(29346)))
    
    print("Current Temperature Set Point = %.1f" % read_float(set_addr))
    
    time.sleep(2)  # small delay just for this demo code
    write_int(16594, 62)  # turn power off, same as pressing Power button on F4T front screen.  Switch must be in EVENT1 position for this to work.
    time.sleep(2)  # small delay just for this demo code
    print("turn off chamber ends")
    
    client.close()

def temp_chamber_set_temp(new_temp_point=24):
    print("####################")
    print("setting chamber temp...")
    client = ModbusTcpClient(address_chamber, port=502)
    
    if client.connect():
        print("Connected to Modbus server successfully")
    else:
        print("Failed to connect to Modbus server")
    
    
    units = read_int(1328)  # read global units, 15=C, 30=F.  This is value displayed on F4T screen
    if units==15:
        print("Global unit is 'C")
    else:
        print("Global unit is 'F")
    
    set_addr = 2782  
    
    print("Chamber Air Temp = %.1f" % (read_float(27586)))
    
    print("Current Temperature Set Point = %.1f" % read_float(set_addr))
    write_float(set_addr, new_temp_point)  # change temperature
    print("New Temperature Set Point = %.1f" % read_float(set_addr))
    print("setting chamber temp. ends")
    time.sleep(2)  # small delay just for this demo code
    
    client.close()


def temp_chamber_wait_settling(checking_time_interval=60, loop_time_out_counts=100, temp_margin=0.1):
    print("####################")
    print("Checking chamber settling...")
    client = ModbusTcpClient(address_chamber, port=502)
    
    if client.connect():
        print("Connected to Modbus server successfully")
    else:
        print("Failed to connect to Modbus server")
    set_addr = 2782  
    temp_chamber_T1=4241
    temp_chamber_T2=4242
    temp_chamber_T3=4243
    temp_chamber_T4=4244
    settling_phase = 0
    i=0
    while True:
        i=i+1
        if i==loop_time_out_counts:
            send_pushbullet_notification("Temp. Chamber Settling Fail.")
            print("Temp. Chamber Settling Fail.")
            return -1
        print("Settling check loop: ", i)
        now_temp = (read_float(27586))
        target_temp = read_float(set_addr)
        print("Current Temperature Set Point = %.1f" % target_temp)        
        print("Chamber Air Temp = %.1f" % now_temp)

        if (target_temp-temp_margin <= now_temp and target_temp+temp_margin >= now_temp):
            settling_phase = settling_phase+1
        else:
            settling_phase = 0
            
        if (settling_phase == 5):
            break
        time.sleep(checking_time_interval)

    print("chamber temp. settlied with margin ", temp_margin)
    time.sleep(2)  # small delay just for this demo code
    now_temp = (read_float(27586))
    send_pushbullet_notification(f"Temp. Chamber Settling Done. Current Temp.: {now_temp}")
    
    client.close()
