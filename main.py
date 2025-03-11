import pyaudio
import json
from vosk import Model, KaldiRecognizer, SetLogLevel
from togetherAPI import callTogether
from centrifuge import spin_centrifuge
import pyttsx3
import time

engine = pyttsx3.init()

# Set log level (optional: -1 to disable debug messages)
SetLogLevel(0)

# Load Vosk model (make sure you have downloaded it)
model = Model(lang="en-us")  # Update this path if necessary

# Initialize recognizer with model and sample rate
recognizer = KaldiRecognizer(model, 16000)
recognizer.SetWords(True)  # Enables word-by-word transcription

# Setup microphone input
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

trying_to_confirm = False
speed = ""
time_spin = ""

print("Listening... Speak into the microphone.")

while True:
    data = stream.read(4096, exception_on_overflow=False)  # Read audio data
    if recognizer.AcceptWaveform(data):  # Full sentence detected
        result = json.loads(recognizer.Result())
        user_message = result.get("text", "")
        print("You said:", user_message)
        
        if "thank you" in user_message:
            break
        
        # Pause the stream while processing API response
        stream.stop_stream()
        
        if trying_to_confirm:
            if "yes" in user_message:
                int_speed = int(speed)
                int_time = int(time_spin)
                print (f"now running at speed {int_speed} and for {time_spin} seconds")
                spin_centrifuge(int_speed, int_time)
                time.sleep(int_time)
                continue
            else:
                trying_to_confirm = False

        # Call API and wait for response
        apiResponse = callTogether(user_message)
        print("API Response:", apiResponse)

        containsSpeed = callTogether(
            f"Does the following message specify what speed to spin the centrifuge? Answer with yes or no: {apiResponse}"
        )
        
        print("Does it contain information on speed?:", containsSpeed)

        
        if 'Yes' in containsSpeed:
            speed = callTogether(
                f"What speed should I set my centrifuge given this information, answer with one integer in rpm, so take the average if you need to: {apiResponse}"
            )
            time_spin = callTogether(
                f"How long should I set my centrifuge given this information, answer with one integer in seconds, so take the average if you need to: {apiResponse}"
            )
            print(f"Would you like to set the centrifuge as the following: Speed (rpm): {speed}, Time (s): {time_spin}")
            time.sleep(3)
            trying_to_confirm = True
            


        # Speak the result
        # engine.say(apiResponse)
        # engine.runAndWait()

        # Resume audio stream for next input
        stream.start_stream()

    else:  # Partial result (real-time feedback)
        partial = json.loads(recognizer.PartialResult())
        print("Partial:", partial.get("partial", ""))

print("Begin centrifuge")
