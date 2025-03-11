import pyaudio
import json
import threading
import time
import serial  
from vosk import Model, KaldiRecognizer, SetLogLevel
from togetherAPI import callTogether
from centrifuge import spin_centrifuge, stop_centrifuge
import pyttsx3

engine = pyttsx3.init()

SetLogLevel(0)

model = Model(lang="en-us")

recognizer = KaldiRecognizer(model, 16000)
recognizer.SetWords(True)

mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

try:
    ser = serial.Serial('COM8', 9600, timeout=1)  
    print("Serial connection established.")
except Exception as e:
    print("Error connecting to serial port:", e)
    ser = None   

trying_to_confirm = False
speed = ""
time_spin = ""
running_centrifuge = False 
stop_flag = threading.Event()  

def centrifuge_thread(speed, duration):
    """
    Runs the centrifuge while listening for stop signals.
    """
    global running_centrifuge
    running_centrifuge = True
    start_time = time.time()

    spin_centrifuge(speed, duration) 

    if ser:
        ser.write(f"SPINNING {speed} RPM for {duration} seconds\n".encode())

    while time.time() - start_time < duration:
        if stop_flag.is_set():
            stop_centrifuge()
            print("Centrifuge stopped manually.")
            if ser:
                ser.write("STOPPED\n".encode())
            running_centrifuge = False
            return
        time.sleep(0.1)  

    print("Finished running.")
    running_centrifuge = False

def serial_monitor_thread():
    """
    Continuously reads data from the serial port and prints it.
    """
    if ser:
        while True:
            try:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print(f"Serial Monitor: {line}")
            except Exception as e:
                print("Serial Read Error:", e)
                break

if ser:
    threading.Thread(target=serial_monitor_thread, daemon=True).start()

print("Listening... Speak into the microphone.")

while True:
    data = stream.read(4096, exception_on_overflow=False) 
    if recognizer.AcceptWaveform(data): 
        result = json.loads(recognizer.Result())
        user_message = result.get("text", "").lower()
        print("You said:", user_message)

        
        if "stop" in user_message and running_centrifuge:
            print("Stop command detected! Stopping centrifuge...")
            stop_flag.set()
            if ser:
                ser.write("STOP COMMAND RECEIVED\n".encode())
            continue

        if "thank you" in user_message:
            break

      
        stream.stop_stream()

        if trying_to_confirm:
            if "yes" in user_message:
                int_speed = int(speed)
                int_time = int(time_spin)
                print(f"Now running at speed {int_speed} rpm for {int_time} seconds.")

           
                stop_flag.clear()

          
                centrifuge_thread_instance = threading.Thread(target=centrifuge_thread, args=(int_speed, int_time))
                centrifuge_thread_instance.start()

                stream.start_stream()
                continue
            else:
                trying_to_confirm = False

     
        apiResponse = callTogether(user_message)
        print("API Response:", apiResponse)

        containsSpeed = callTogether(
            f"Does the following message specify what speed to spin the centrifuge? Answer with yes or no: {apiResponse}"
        )

        print("Does it contain information on speed?:", containsSpeed)

        if 'yes' in containsSpeed.lower():
            speed = callTogether(
                f"What speed should I set my centrifuge given this information? Answer with one integer in rpm: {apiResponse}"
            )
            time_spin = callTogether(
                f"How long should I set my centrifuge given this information? Answer with one integer in seconds: {apiResponse}"
            )
            print(f"Would you like to set the centrifuge as the following: Speed (rpm): {speed}, Time (s): {time_spin}")
            time.sleep(3)
            trying_to_confirm = True

        stream.start_stream()

    else:
        partial = json.loads(recognizer.PartialResult())
        print("Partial:", partial.get("partial", ""))

print("Begin centrifuge")
