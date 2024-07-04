"""
This program is written in Python 3.11.6 by Yannic Altmann to record 
measurements at the deposition process test site using the IL150.
"""
# Import modules
import serial
from serial.tools import list_ports 
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import winsound

#### Define the parameters of the measurement ####

# Define the measurement identifier:
sample = "Sample"
temperature = "100C"
MEASUREMENT = f"{sample}_{temperature}_{time.strftime('%y%m%d_%H%M%S', time.localtime())}"

# Set measurement parameters:
duration = 300      # Measurement duration in seconds
heating_time = 10   # Waiting time bevore measurement in minutes 
density = 1.238     # Density of the evaporant

####  ####

# Defining necessary functions
def initiate_crystal(port) -> serial.Serial:
    """Opens the conection to the IL150 device via a given COM-Port and returns a serial instance."""
    ports = [comport.device for comport in list_ports.comports()] # list available COM-Ports for problem analysis
    try: 
        ser = serial.Serial(port, baudrate=4800, bytesize=7, parity=serial.PARITY_EVEN, stopbits=2, timeout=10)  # open serial port
        print(f"Connected via {ser.name}.") 
    except:
        raise ConnectionError(f"The device could not be initiated, maybe try another COM-port from the list: {ports}") 
    if ser.rts == False: # check for reading access 
        print("\033[0;31mWarning\033[0m: Reading might be disabled!")
        print(f"Maybe try another COM-port from the list: {ports}")
    if ser.cts == False: # check for writing access
        print("\033[0;31mWarning\033[0m: Writing might be disabled!")
        print(f"Maybe try another COM-port from the list: {ports}")
    return ser

def read_freqency(serial: serial.Serial) -> float:
    """Reads the curent crystal frequency from a IL150 serial instance and returns it."""
    serial.write("CX\r".encode())                   # write the check crystal command
    return_code = serial.read_until("\r".encode())
    if int(return_code.decode()) == 0:              # check for successful comunication
        x_numb = serial.read_until("\r".encode())   # read the crystal number
        x_freq = serial.read_until("\r".encode())   # read the crystal frequency
    else:
        raise ValueError("The command was not recived correctly.")
    return float(x_freq.decode())

def run_measurement(serial: serial.Serial, duration = 300) -> tuple[list, list]:
    """Records the crystal frequency from a IL150 serial instance over a given time in seconds and returns times and frequencies as lists."""
    # initiate required lists and variables 
    times = []
    freqencies = []
    progress = 1

    serial.write("TL\r".encode())       # write the test layer command
    return_code = serial.read_until("\r".encode())
    if int(return_code.decode()) != 0:  # check for successful comunication
        serial.close()
        raise ValueError("The command was not recived correctly.")

    for sec in range(duration):
        freq = read_freqency(serial)                # get the current frequency
        freqencies.append(freq)
        times.append(sec)
        if (sec % (duration/10) == 0 and sec != 0): # return progress to console
            print(f"{progress * 10}% done.")
            progress += 1
        time.sleep(1)

    serial.write("SC\r".encode())       # write the shutter close command
    return_code = serial.read_until("\r".encode())
    if int(return_code.decode()) != 0:  # check for successful comunication
        serial.close()
        raise ValueError("The command was not recived correctly.")
    
    serial.close() # close the serial instance
    return times, freqencies

def calc_thicknes(frequencies: list, density: float) -> list:
    """Takes the list of frequencies (over time) and the density of the evaporant [g/cm**3] and returns the list of thicknes (over time)."""
    # Initiate required lists and variables 
    delta_f = np.zeros(len(frequencies))
    d_q = 0.003     # Thicknes of the quarz in [m]
    roh_q = 2.65    # Density of the quarz in [g/cm**3]
    for ind in range(len(frequencies)):
        delta_f[ind] = frequencies[ind] - frequencies[0]
    thicknes = - delta_f * d_q/frequencies[0] * roh_q/density 
    return thicknes

def plot_results(time: list, frequency: list, thicknes: list) -> None:
    """Takes the time, frequency and thicknes values and plots these into a plt.Figure"""
    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax1.plot(np.asarray(time)/60, np.asarray(frequency)/(10**6), label="Crystal Freq.")
    ax1.set_title("Frequency")
    ax1.set_xlabel("Time [min]")
    ax1.set_ylabel("Frequency [MHz]")
    ax2 = fig.add_subplot(122)
    ax2.set_title("Thicknes")
    ax2.set_xlabel("Time [min]")
    ax2.set_ylabel("Thicknes [nm]")
    ax2.plot(np.asarray(time)/60, np.asarray(thicknes)*10**9, label="Thicknes")
    plt.show()

def save_results(time: list, frequency: list, thicknes: list) -> None:
    """Takes the time, frequency and thicknes values and writes them into a .csv file."""
    df = pd.DataFrame(zip(time,frequency,thicknes), columns=["Time", "Frequency", "Thicknes"])
    df.to_csv(f"{MEASUREMENT}.csv", index=False)


# Main workflow through the measurement: 
time.sleep(heating_time * 60)
winsound.Beep(1000, 1000)
ser = initiate_crystal("COM7")
times, frequencies = run_measurement(ser, duration)
total_thicknes = calc_thicknes(frequencies, density)
plot_results(times, frequencies, total_thicknes)
save_results(times, frequencies, total_thicknes)
for i in range(3):
    winsound.Beep(1000, 300)
    time.sleep(0.033)

