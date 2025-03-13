User Interface Set-Up
The Raspberry Pi 5 hosts both the python script that handles speech to text and Together.ai API and the arduino program that communicates with the arduino. To set up the Raspberry Pi 5:

1. Follow this tutorial on how to set up the Pi and install OS system and Arduino IDE: Raspberry Pi 5 Setup: Getting Started Guide (Step By Step)
2. Pull code from https://github.com/mliu1204/bio123v3
3. Create Together.ai key and put in a .env folder with TOGETHER_API_KEY=“”
4. Connect and run Arduino code, make sure the serial monitor is closed
   a. You can check if connection is well established by typing RPM space duration (“2000 60” = 2000 RPM for 60 seconds) into the serial monitor, make sure to close it before running the python script
5. Make sure the “port” variable in the centrifuge.py file is set correctly, check comment for specifics.
6. Connect all peripherals, run main.py with Thonny, run v3.ino with Arduino IDE
   a. Follow prompts in the terminal. Type stop into serial monitor if you need to stop mid cycle
