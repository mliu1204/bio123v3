import serial
import time


def spin_centrifuge(duration, speed):
    # Replace 'COM3' with your actual serial port (e.g., '/dev/ttyUSB0' on Linux/Mac)
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  
    time.sleep(2)  # Wait for the connection to establish

    # Data to send
    data = f"{duration} {speed}"

    # Send data followed by a newline character (optional, based on receiver behavior)
    ser.write((data + "\n").encode())  

    # Close the serial connection
    ser.close()
    
spin_centrifuge(100, 100)

