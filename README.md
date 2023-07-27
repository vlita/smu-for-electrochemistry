
# Electrolysis with Keithley 2401 SMU
![](https://i.imgur.com/CvJNywC.gif)
This repository is intended for the python-friendly chemist who wants to perform real-time measurements on a two-electrode cell using Keithley’s Standard Series 2401 Source Measure Unit. Galvanostatic and potentiostatic methods of electrolysis are supported, as well as a method for two-electrode cyclic voltammetry. Instrument cannot exceed 20V/1A.

## Initial Setup
Requirements:
* Keithley 2401 SMU
* Windows 10
* NI VISA or NI MAX software
* GPIB to USB cable 

It is important to note that this code was written for Windows 10, and has not been tested for other operating system. Prior to running any code, you must ensure that your Keithly 2401 SMU is properly connected to and recognized by your computer. A GPIB to USB cable is required for this purpose. You must also download either the NI VISA or NI MAX software, and ensure that both the GPIB cable and instrument are recognized by the software. Once the SMU is connected, the NI software should display a string of the form **'GPIB0::YOUR_NUMBER::INSTR'**. Be sure to save this string, as it will be important later. 
## Installation

Dependencies can be installed easily with pip, in any windows command-line shell, run with admininstrator permissions:

```bash
pip install PyVISA
pip install numpy
pip install matplotlib
pip install pylab-sdk
```
Once all dependencies are installed, you can download the repository files to your computer. Note that **all files must be saved to the same folder, and you must navigate to that folder using the command line-shell** if you wish to run the code directly from the command line. Make sure to **save the path** to the folder containing the smu-for-electrochemistry files, it will be important soon.
## Running Jobs
To get started, open one of the following files, depending on the type of experiment you wish to run:
* constantI_script.py
* constantV_script.py
* cyclic_voltammetry_script.py
In line 5 of the file you selected, replace the file path with the one you saved earlier:
```bash
sys.path.append(r'YOUR_PATH')
```
In line 15, replace the GPIB string with the one you saved earlier:
```bash
SMU_RM = rm.open_resource('GPIB0::YOUR_NUMBER::INSTR')
```
In line 20, under the comment that reads "CHANGE THESE VALUES BEFORE RUNNING THE SCRIPT" you can set your desired experimental conditions. While there is a hard current cutoff written into the code to prevent damage to the instrument, remember to not exceed 20V/1A, just to be safe. 

Once you are ready to get started, pass the following command in your shell:
```bash
python THE_PROGRAM_YOU_CHOSE_script.py
```
That's it! Your plots should automatically open and begin displaying data! Once the program is finished, your plots and data will be saved in the current folder. 

**NOTE: Before performing any experiment on an electrochemical system, you should test the program is doing what you expect by connecting your SMU to a resistor and running at least one of the above scripts.**



## Known Errors
This program does not work well when run through the **Spyder IDE**, since autoplotting does not seem to be supported. 

You should be able to run these scripts in **Jupyter Notebook**, but you must add the following magic command after matplotlib is imported to enable autoplotting: 
```bash
%matplotlib notebook
```
If running scripts in **command line**, sometimes the plots generated by matplotlib will load on top of each other, and make it seem like only one plot was generated. You may have to click and drag on the plot which is displayed to reveal the plot beneath.  
## Acknowledgements
A huge thank you to Aaron Hagerstrom, who not only wrote the initial version of the Keithley2401_voltmeter program, but also helped me troubleshoot my code. This project would not have been possible without him.
