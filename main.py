import ctrl_func
import math
import numpy as np
import time
import re
import sys

# Chamber control codes

address_chamber = "192.168.XXX.XXX" # Get yout chamber IP from the device setting menu.
client = ModbusTcpClient(address_chamber, port=502)
temp_chamber_check()
temp_chamber_power_on()
temp_chamber_set_temp(new_temp_point=27)
temp_chamber_wait_settling(checking_time_interval=30, loop_time_out_counts=30, temp_margin=0.1) 
# check the temp. is settled as you want. Chamber checks temp. for 'loop_time_out_counts' times at every 'checking_time_interval' interval
# if the measured temperature is settled within the 'temp_margin' for 5 time, it sends notification to your phone.
temp_chamber_power_off()
print("done")
