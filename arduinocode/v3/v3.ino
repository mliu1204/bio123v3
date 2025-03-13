const byte COMPARATOR = 2;
const byte motor_gate_pin = 9;
int signalCount = 0;
bool comparatorState = HIGH;
unsigned long prevSignalTime = 0;
float prevRPM = 0;
int write_duty = 0;
float targetRPM = 0;
unsigned long runDuration = 0;
unsigned long startTime = 0;
bool motorRunning = false;
unsigned long lastRPMCheckTime = 0;
const unsigned long rpmTimeout = 1000; // 1 second timeout for no RPM detection

// PID Control Variables
float Kp = 0.05;   // Proportional gain
float Ki = 0.01;   // Integral gain
float Kd = 0.02;   // Derivative gain
float integral = 0;
float prevError = 0;
const int minDutyIncrease = 10;
const int maxIntegral = 50;  // Prevent integral wind-up

void switchPressed() {
    bool currentState = digitalRead(COMPARATOR);
    if (currentState == LOW && comparatorState == HIGH) {
        signalCount++;
    }
    comparatorState = currentState;
}

void setup() {
    pinMode(motor_gate_pin, OUTPUT);
    pinMode(COMPARATOR, INPUT_PULLUP);
    Serial.begin(9600);
    prevSignalTime = millis();
    lastRPMCheckTime = millis();
}

void loop() {
    if (Serial.available()) {
        String input = Serial.readStringUntil('\n');
        input.trim();
        
        if (input.equalsIgnoreCase("stop")) {
            Serial.println("Stopping motor...");
            analogWrite(motor_gate_pin, 0);
            motorRunning = false;
            return;
        }
        
        int spaceIndex = input.indexOf(' ');
        if (spaceIndex != -1) {
            targetRPM = input.substring(0, spaceIndex).toFloat();
            runDuration = input.substring(spaceIndex + 1).toInt() * 1000; // Convert to milliseconds
            Serial.print("Target RPM: ");
            Serial.println(targetRPM);
            Serial.print("Run Duration (ms): ");
            Serial.println(runDuration);
        } else {
            Serial.println("Invalid input. Please enter in format: RPM TIME");
            return;
        }
        
        Serial.println("Starting centrifuge...");
        startTime = millis();
        write_duty = 140; // Initial PWM to ensure smooth start
        analogWrite(motor_gate_pin, write_duty);
        delay(500);
        motorRunning = true;
        attachInterrupt(digitalPinToInterrupt(COMPARATOR), switchPressed, CHANGE);
    }

    if (motorRunning && millis() - startTime >= runDuration) {
        Serial.println("Run complete. Stopping motor.");
        analogWrite(motor_gate_pin, 0);
        motorRunning = false;
    }

    if (motorRunning && signalCount >= 10) {
        float cur_time = millis();
        float timeLapsed = cur_time - prevSignalTime;
        prevSignalTime = cur_time;
        float rpm = (signalCount / timeLapsed) * 1000 * 60 / 2;
        signalCount = 0;
        lastRPMCheckTime = millis();
        
        // PID Control
        float error = targetRPM - rpm;
        integral += error;
        integral = constrain(integral, -maxIntegral, maxIntegral); // Prevent wind-up
        float derivative = error - prevError;
        prevError = error;

        int adjustment = Kp * error + Ki * integral + Kd * derivative;
        write_duty = constrain(write_duty + adjustment, 0, 255);
        analogWrite(motor_gate_pin, write_duty);

        Serial.print("Current RPM: ");
        Serial.print(rpm);
        Serial.print(" | Target RPM: ");
        Serial.print(targetRPM);
        Serial.print(" | PWM: ");
        Serial.print(write_duty);
        Serial.print(" | Kp: ");
        Serial.print(Kp);
        Serial.print(" | Ki: ");
        Serial.print(Ki);
        Serial.print(" | Kd: ");
        Serial.print(Kd);
        Serial.print(" | Integral: ");
        Serial.print(integral);
        Serial.print(" | Derivative: ");
        Serial.println(derivative);
    }
    
    // If no RPM is detected for more than 1 second, increase duty cycle
    if (motorRunning && millis() - lastRPMCheckTime > rpmTimeout) {
        Serial.println("No RPM detected, increasing duty cycle.");
        write_duty = constrain(write_duty + minDutyIncrease, 0, 255);
        analogWrite(motor_gate_pin, write_duty);
        lastRPMCheckTime = millis(); // Reset timeout timer
    }
}
