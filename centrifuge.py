import serial
import time

port = 'COM8' #change to this when using raspbarry pi: /dev/ttyACM0, use this when using windows: COM8

def stop_centrifuge():
    ser = serial.Serial(port, 9600, timeout=1)  
    time.sleep(2)

    data = "stop" 

    # Send data followed by a newline character (optional, based on receiver behavior)
    ser.write((data + "\n").encode())  

    # Close the serial connection
    ser.close()

def spin_centrifuge(duration, speed):
    # Replace 'COM3' with your actual serial port (e.g., '/dev/ttyUSB0' on Linux/Mac)
    ser = serial.Serial(port, 9600, timeout=1)  #change to this when using raspbarry pi: /dev/ttyACM0, use this when using windows: COM8
    time.sleep(2)  # Wait for the connection to establish

    # Data to send
    data = f"{duration} {speed}"

    # Send data followed by a newline character (optional, based on receiver behavior)
    ser.write((data + "\n").encode())  

    # Close the serial connection
    ser.close()
    
