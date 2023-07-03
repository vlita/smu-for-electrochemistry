#constant voltage, read current

#initial stetup
import sys
sys.path.append(r'Desktop\SMU_files\\')
import Keithley2401_voltmeter_063023 as K2401
import pyvisa
import time
import datetime
import csv
import numpy as np
import matplotlib.pyplot as plt

rm = pyvisa.ResourceManager()
SMU_RM = rm.open_resource('GPIB0::3::INSTR')
SMU = K2401.Keithley2401(SMU_RM)
SMU.initial_setup()
plt.ion()

#CHANGE THESE VALUES BEFORE RUNNING THE SCRIPT
time0 = time.time()
voltage_level = 3 # set a constant voltage
measurement_time = 10 # number of seconds to perform measurement
num_readings = 20 # number of data points to collect
wait_time = measurement_time/num_readings # wait time between measurements in seconds

NPLC = 1
V_range = 20 # voltage range
I_compliance = 1e-1 # max current
V_compliance = 5 # max voltage
init_wait = 0.25 # does not do anything yet
SMU.setup_single_Imeas(NPLC = NPLC, V_range = V_range, V_compliance = V_compliance, I_compliance = I_compliance, voltage_level = voltage_level, init_wait = init_wait)
SMU.turn_on()

#initializes dynamically updating plots
vc = K2401.DynamicUpdateOG()
tc = K2401.DynamicUpdateOG()

vc.on_launch("voltage (V)", "current (mA)")
tc.on_launch("time (s)", "current (mA)")

#creates lists to store data
currents = []
times = []
voltages = []

#generates data and accounts for time lag
for i in range(1,num_readings):
    time_1 = time.time()
    
    I,V = SMU.single_Vmeas()
    currents.append(I)
    voltages.append(V)
    times.append(time.time()-time0)
    vc.on_running(voltages, currents)
    tc.on_running(times, currents)
    
    time_2 = time.time()
    time_error = time_2 - time_1
    
    if time_error < wait_time:
        time.sleep(wait_time - time_error)
    else:
        time.sleep(time_error)

SMU.turn_off()

#stores data and prints a figure displaying current vs. time
tc.on_completion("CP", F'{voltage_level}volt', voltages, currents, times, currents)