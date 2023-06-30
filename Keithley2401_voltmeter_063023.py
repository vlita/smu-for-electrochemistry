import time
import pyvisa
import numpy as np
import pylab as pl
import matplotlib.pyplot as plt

# set maximum allowed current and voltage to prevent user typos from breaking anything
SMU_I_HARD_MAX = 10e-3

class Keithley2401():
    
    def __init__(self, visa_resource):
        self.visa_resource = visa_resource
        self.num_readings = None
        self.current_output_setting = None
        self.info_dict = {}
        self.info_dict["model_number"] = "Keithley2401"
        self.info_dict["serial_number"] = "Unknown"
        self.info_dict["resource_name"] = self.visa_resource.resource_name
    
    def write(self, txt):
        self.visa_resource.write(txt)

    def read(self):
        return self.visa_resource.read()

    def query(self, txt):
        return self.visa_resource.query(txt)

    def get_info(self):
        '''
        Returns intrument metadata you may want to keep track of.
        
        Returns
        -------
        info_dict : dict
            keys: ex. "GPIB address"
            values: ex. 11
        '''
        return self.info_dict
    
    def initial_setup(self):
        '''
        call at the beginning of a measurement to put the SMU in a known state
        '''
        self.write("*RST;") #reset settings to default
        
        # clears standard event register, operation event resiter, measurment event register, questionable event register
        self.write("*CLS;") 
    
        # I think this is the same thing as *RST
        # SMU.write(":SYSTem:PRESet;")
        
        # you can turn off autozero to make measurements faster
        # but you will loose accuracy
        # SMU.write(":SYST:AZER OFF;") 
        
        # output stays on until you explicitly turn it off
        self.write(":SOUR:CLE:AUTO OFF;")
        
        # disable beeper
        self.write(":SYST:BEEP:STAT 0;")
        
        # set system time to 0
        self.write(':SYSTem:TIME:RESet');
        
        #clear trigger
        self.write(':TRIGger:CLEar');
        
        # 4-wire mode
        self.write(":SYST:RSEN ON;")
        
        # turn off all measurements
        self.write(":SENS:FUNC:OFF:ALL;")
        
        # turn on voltage measurement
        self.write(":SENS:FUNC 'VOLT';")
        
        # turn on current measurement
        self.write(":SENS:FUNC 'CURR';")
        
        #set arm and trigger to actiavate immmediatly
        #SMU.write(':ARM:SOURce IMMediate')
        #SMU.write(':TRIG:SOUR IMMediate')
        #SMU.write(':TRIG:OUT SOURce')

#     def sweep_setup(self, NPLC = 10, C_compliance = 10e-3):
#         # set NPLC
#         self.write(":SENS:CURR:NPLC {};".format(NPLC))
#         self.write(":SENS:VOLT:NPLC {};".format(NPLC))
#         # configure output mode, range, and compliance for smu
        
#         # set current reading range to auto
#         self.write(":SOUR:FUNC:MODE VOLT")
#         self.write(":SENS:CURR:PROT:LEV " + str(C_compliance))
#         self.write(":SENS:CURR:RANGE:AUTO 1")
  
     
    def setup_timeseries_Vmeas(self, NPLC = 10, I_range = 10e-3, V_compliance = 3, current_list = [0], init_wait = 0.25):
        '''
        call to change measurement configuration
        '''

        # set NPLC
        self.write(":SENS:CURR:NPLC {};".format(NPLC))
        self.write(":SENS:VOLT:NPLC {};".format(NPLC))
        # configure output mode, range, and compliance for smu
        
        # set to source current
        self.write(":SOUR:FUNC CURR;")
        
        # set current range
        self.write(":SOUR:CURR:RANG "+str(I_range)+" ;")
        
        # measurement range is on the same range as compliance
        self.write(":SENS:VOLT:PROT:RSYN ON;")
        self.write(":SENS:VOLT:PROT "+str(V_compliance))
    
        # validate current settings
        is_number = True
        in_range = True
        
        self.num_readings = len(current_list)
        for I in current_list:
            if not np.can_cast(type(I),np.floating):
                is_number = False
                
            if np.abs(I)>SMU_I_HARD_MAX:
                in_range = False
            
        good = in_range and is_number
        if not good:
            raise(ValueError("Invalid current list"))
        
        self.write(":SOURce:CURR:MODE LIST")
        self.write(":SOUR:LIST:CURR {}".format(current_list[0])) 
        for current in current_list[1:]:
            self.write(":SOUR:LIST:CURR:APP {}".format(current))
        
        # when triggered, take self.num_readings measurements
        self.write(":TRIG:COUN {}".format(self.num_readings))
        
    def setup_timeseries_Imeas(self, NPLC = 10, V_range = 2, V_compliance = 5, I_compliance = 1e-1, voltage_list = [0], init_wait = 0.25):
        '''
        call to change measurement configuration
        '''

        # set NPLC
        self.write(":SENS:CURR:NPLC {};".format(NPLC))
        self.write(":SENS:VOLT:NPLC {};".format(NPLC))
        # configure output mode, range, and compliance for smu
        
        # set to source voltage
        self.write(":SOUR:FUNC VOLT;")
        
        # set voltage range
        self.write(":SOUR:VOLT:RANG "+str(V_range)+" ;")
        
        # measurement range is on the same range as I_compliance
        self.write(":SENS:CURR:PROT:RSYN ON;")
        self.write(":SENS:CURR:PROT "+str(I_compliance))
        
        # validate current settings
        is_number = True
        in_range = True
        
        self.num_readings = len(voltage_list)
        for V in voltage_list:
            if not np.can_cast(type(V),np.floating):
                is_number = False
                
            if np.abs(V)>V_compliance:
                in_range = False
            
        good = in_range and is_number
        if not good:
            raise(ValueError("Invalid current list"))
        
        self.write(":SOURce:VOLT:MODE LIST")
        self.write(":SOUR:LIST:VOLT {}".format(voltage_list[0])) 
        for voltage in voltage_list[1:]:
            self.write(":SOUR:LIST:VOLT:APP {}".format(voltage))
        
        # when triggered, take self.num_readings measurements
        self.write(":TRIG:COUN {}".format(self.num_readings))
        
    def initiate_timeseries_Vmeas(self):
        self.write(':READ?')
        
    def initiate_timeseries_Imeas(self):
        self.write(':READ?')
    
    def turn_on(self):
        self.write(":OUTP ON")

    def turn_off(self):
        self.write(":OUTP OFF;")
    

    # todo: make this do something
    def raise_errors(self):
        raise NotImplementedError

    def setup_single_Vmeas(self, NPLC = 10, I_range = 10e-3, V_compliance = 3, current_level = 0, init_wait = 0.25):

        # set NPLC
        self.write(":SENS:CURR:NPLC {};".format(NPLC))
        self.write(":SENS:VOLT:NPLC {};".format(NPLC))
        # configure output mode, range, and compliance for smu
        
        # set to source current
        self.write(":SOUR:FUNC CURR;")
        
        # set current range
        self.write(":SOUR:CURR:RANG "+str(I_range)+" ;")
        
        # measurement range is on the same range as compliance
        self.write(":SENS:VOLT:PROT:RSYN ON;")
        self.write(":SENS:VOLT:PROT "+str(V_compliance))
        is_number = True
        in_range = True
        
        # validate current setting
        if not np.can_cast(type(current_level),np.floating):
            is_number = False
                
        if np.abs(current_level)>SMU_I_HARD_MAX:
                in_range = False
                
        good = in_range and is_number
        if not good:
            raise(ValueError("Invalid current setting"))
        
        self.num_readings = 1
        self.write(":SOURce:CURR:MODE FIXED")
        self.write(":SOUR:CURR:LEV {}".format(current_level))
        self.write(":TRIG:COUN {}".format(self.num_readings))
    
    def setup_single_Imeas(self, NPLC = 10, V_range = 2, V_compliance = 5, I_compliance = 1e-1, voltage_level = 0, init_wait = 0.25):
        
        # set NPLC
        self.write(":SENS:CURR:NPLC {};".format(NPLC))
        self.write(":SENS:VOLT:NPLC {};".format(NPLC))
        # configure output mode, range, and compliance for smu
        
        # set to source voltage
        self.write(":SOUR:FUNC VOLT;")
        
        # set voltage range
        self.write(":SOUR:VOLT:RANG "+str(V_range)+" ;")
        
        # measurement range is on the same range as I_compliance
        self.write(":SENS:CURR:PROT:RSYN ON;")
        self.write(":SENS:CURR:PROT "+str(I_compliance))
        is_number = True
        in_range = True
        
        # validate voltage setting
        if not np.can_cast(type(voltage_level),np.floating):
            is_number = False
                
        if np.abs(voltage_level)>V_compliance:
                in_range = False
                
        good = in_range and is_number
        if not good:
            raise(ValueError("Invalid voltage setting"))
        
        self.num_readings = 1
        self.write(":SOURce:VOLT:MODE FIXED")
        self.write(":SOUR:VOLT:LEV {}".format(voltage_level))
        self.write(":TRIG:COUN {}".format(self.num_readings))
        
    def read_data(self, time_column_name = "timestamp", v_column_name = "Voltage (V)", i_column_name = "Current (A)"):
        data = self.read()
        nums = np.array([float(x) for x in data.split(",")])
        volts_index = np.array((0 + np.arange(self.num_readings)*5),dtype = "int64")
        curr_index = np.array((1 + np.arange(self.num_readings)*5),dtype = "int64")
        time_index = np.array((3 + np.arange(self.num_readings)*5),dtype = "int64")
        voltages = nums[volts_index]
        currents = nums[curr_index]
        times = nums[time_index]
    
        out = None
        if self.num_readings == 1:
            voltage = voltages[0]
            current = currents[0]
            #times = times[0]
            out = current, voltage
        
        else:
            out = {}
            out[time_column_name] = times
            out[i_column_name] = currents
            out[v_column_name] = voltages
        
        return out
    
    # todo: make this do something
    def wait_for_data(self):
        pass
    
    def single_Vmeas(self):
        self.write(':READ?')
        return self.read_data()
    
    def single_Imeas(self):
        self.write(':READ?')
        return self.read_data()
    
    def fetch_timeseries_Vmeas(self, time_column_name = "timestamp", v_column_name = "Voltage (V)", i_column_name = "Current (A)"):
        #SMU_columns = ["Time", "Current (mA)", "Voltage (V)"]
        self.wait_for_data()
        return self.read_data(time_column_name, v_column_name, i_column_name)
    
#%%
if __name__ == "__main__":
    NPLC = 1
    I_range = 10e-3
    V_compliance = 5 
    num_readings = 50
    init_wait = 0.25 # does not do anything yet
    current_level = 1e-3
    
    rm=visa.ResourceManager()
    SMU_RM = rm.open_resource('GPIB0::3::INSTR')
    SMU = Keithley2401(SMU_RM)
    SMU.initial_setup()
    #%%
    # do a single measurement
    SMU.setup_single_Vmeas(NPLC = NPLC, I_range = I_range, V_compliance = V_compliance, current_level = current_level, init_wait = init_wait)
    SMU.turn_on()
    
    time0 = time.time()
    set_currents = np.linspace(0,3e-3,20)
    currents = np.zeros(len(set_currents))
    voltages = np.zeros(len(set_currents))
    times = np.zeros(len(set_currents))
    for i, current_level in enumerate(set_currents):
        #SMU.setup_single_Vmeas(NPLC = NPLC, I_range = I_range, V_compliance = V_compliance, current_level = current_level, init_wait = init_wait)
        I,V = SMU.single_Vmeas()
        voltages[i] = V
        currents[i] = I
        time.sleep(1)
        times[i] = time.time()-time0
        
    pl.figure()
    pl.plot(currents*1000.0,voltages, marker = 'o')
    pl.xlabel("current (mA)")
    pl.ylabel("voltage (V)")
    pl.show()
    
    pl.figure()
    pl.plot(times,voltages, marker = 'o')
    pl.xlabel("time (s)")
    pl.ylabel("voltage (V)")
    pl.show()
    #%%
    current_list = [1e-3]*10 + [2e-3]*10
    SMU.setup_timeseries_Vmeas(NPLC = 10, I_range = 10e-3, V_compliance = 3, current_list = current_list, init_wait = 0.25)
    #%%
    SMU.write(":READ?")
    SMU.write("*OPC")
    #%%
    out_data = SMU.fetch_timeseries_Vmeas()
    
    pl.figure()
    pl.plot(out_data['timestamp'],out_data['Current (A)'], marker = 'o')
    pl.xlabel("time (s)")
    pl.ylabel("voltage (V)")
    pl.show()
    
    SMU.turn_off()
    # do a list measurement 
    #SMU.initial_setup()
    #SMU.setup_timeseries_Vmeas(NPLC,V_range,num_readings,current,init_wait)
    #SMU.initiate_timeseries_Vmeas()
    #SMU_data = SMU.fetch_timeseries_Vmeas()
    #SMU.setup_single_Vmeas(NPLC, V_range)
    #single = SMU.single_Vmeas()
    
    #print(SMU_data)
    #print(single)

class DynamicUpdateOG():
    
    def on_launch(self, x_label, y_label):
        #set up plot
        self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([],[], 'o')
        #set up axis which scale with data
        self.ax.set_autoscalex_on(True)
        self.ax.set_autoscaley_on(True)
        #set up figure labels
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.grid
        ...

    def on_running(self, xdata, ydata):
        #update data (with the new _and_ the old points)
        self.lines.set_xdata(xdata)
        self.lines.set_ydata(ydata)
        #need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        #we need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        
    def on_completion(self, fname, level, var1, var2, var3, var4):
        #saves data to a .png file
        from datetime import date
        d = date.today()
        self.figure.tight_layout
        self.figure.savefig(F'{d.strftime("%Y_%m_%d")}_{fname}_{level}.png', dpi = 300, bbox_inches = 'tight')
        np.savetxt(F'{d.strftime("%Y_%m_%d")}_{fname}_data_{level}.csv', np.c_[np.asarray(var1), np.asarray(var2)], delimiter = ',')
        np.savetxt(F'{d.strftime("%Y_%m_%d")}_{fname}_vs_time_data.csv', np.c_[np.asarray(var3), np.asarray(var4)], delimiter = ',')

class DynamicUpdateCV():
    
    def on_launch(self, x_label, y_label, min_x, max_x):
        #set up plot
        self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([],[], 'o')
        #set up axis which scale with data
        self.ax.set_autoscaley_on(True)
        self.ax.set_xlim(min_x, max_x)
        #set up figure labels
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.grid
        ...

    def on_running(self, xdata, ydata):
        #update data (with the new _and_ the old points)
        self.lines.set_xdata(xdata)
        self.lines.set_ydata(ydata)
        #need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        #we need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        
    def on_completion(self, fname, volt_range, scan, var1, var2):
        #saves data to a .png file
        from datetime import date
        d = date.today()
        self.figure.tight_layout
        self.figure.savefig(F'{d.strftime("%Y_%m_%d")}_{fname}_{volt_range}_{scan}.png', dpi = 300, bbox_inches = 'tight')
        np.savetxt(F'{d.strftime("%Y_%m_%d")}_cyclic_voltammetry_data_{volt_range}_{scan}.csv', np.c_[np.asarray(var1), np.asarray(var2)], delimiter = ',')

class vlist():
    #creates a list of voltages the program will iterate through, 
    def generate(self, initial_voltage, final_voltage, scan_rate, cycles):
        self.voltage_range = []
        self.set_voltages_list = list(np.arange(initial_voltage, final_voltage, scan_rate))
        self.set_voltages_list.append(final_voltage)
        self.set_voltages_list_itr = self.set_voltages_list[:-1] + list(reversed(self.set_voltages_list[1:]))

        for c in range(0, cycles):
            self.voltage_range = self.voltage_range + self.set_voltages_list_itr

        self.voltage_range.append(initial_voltage)
    
        return self.voltage_range