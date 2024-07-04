# Autosave for Agilent Oscilloscope
# Written by Marcel Schlesag and Yannic Altmann

# Modules
import pyvisa
import time
import datetime
import keyboard

def initialize_oscilloscope(format: str="CSV", length: int=1000, segment: str="CURR") -> object:
    """initialize oscilloscope with principal save settings"""
    global inst 
    rm = pyvisa.ResourceManager('@py')
    print(rm.list_resources())
    try:
    # Instatiate Oscilloscope Settings
        inst = rm.open_resource("TCPIP::169.254.254.254::INSTR")
        print(inst.query("*IDN?"))
    # Setup Save Settings
        inst.write("SAVE:PWD '/usb0/'")
        inst.write(f":SAVE:WAVeform:FORMat {format}")
        inst.write(f":SAVE:WAVeform:LENGth {length}")
        inst.write(f":SAVE:WAVeform:SEGMented {segment}")
    # Return Instrument
        print("Successfuly initialized, program is running.")
        return inst
    except: raise ReferenceError("Oscilloscope could not be initialized.")

def save_oscilloscope_data(samplename):
    """saves oscilloscope data to USB"""
    today = datetime.datetime.today()
    today_str = today.strftime("%y%m%d_%H%M%S")
    inst.write(f"SAVE:FILename '{samplename}_{today_str}'")
    inst.write(":SAVE:WAVeform:STARt")
    print(f"File {samplename}_{today_str} saved to USB.")

def is_triggered() -> bool:
    """checks if oscilloscope has been triggered"""
    return bool(int(inst.query(":TER?")))

def break_junction_measurement(sample, counter=0):
    """measure V(t) profile for break junctions"""
    inst = initialize_oscilloscope()
    while True:
        # Oscilloscope Trigger
        status = is_triggered()
        if status == True:
            print("Oscilloscope has triggered.")
            time.sleep(float(inst.query(":TIMebase:RANGe?").strip())/10 * 6)
            save_oscilloscope_data(sample)
            counter += 1
            time.sleep(2)
            print(f"Measured Curves: {counter}.\n")
            continue
        # Break Condition
        if keyboard.is_pressed("esc") is True:
            break
        # Wait Condition
        else: 
            time.sleep(0.05)

    print("Program has been terminated successfully.")

# Main
# Sample should not have more than six characters!
break_junction_measurement(sample="sample")
