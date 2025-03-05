import pyaudio
import json
from vosk import Model, KaldiRecognizer, SetLogLevel
from togetherAPI import callTogether
import pyttsx3

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

print("Listening... Speak into the microphone.")

while True:
    data = stream.read(4096, exception_on_overflow=False)  # Read audio data
    if recognizer.AcceptWaveform(data):  # Full sentence detected
        result = json.loads(recognizer.Result())
        user_message = result.get("text", "")
        print("You said:", user_message)
        if  "thank you" in user_message:
            break
        apiResponse = callTogether(user_message)
        print(apiResponse)
        
        containsSpeed = callTogether("does the following messsage have what speed to spin the centrifuge, answer with yes or no: " + apiResponse)
        print("does it contain information on speed?: " + containsSpeed)

        # speak the result
        engine.say(apiResponse)
        engine.runAndWait()
    else:  # Partial result (real-time feedback)
        partial = json.loads(recognizer.PartialResult())
        print("Partial:", partial.get("partial", ""))

print("begin centrifuge")