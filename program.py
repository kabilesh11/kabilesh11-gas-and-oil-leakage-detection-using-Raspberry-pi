import time
import RPi.GPIO as GPIO
from pushbullet import Pushbullet
import configparser

# Set GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the GPIO pins connected to the analog outputs of the gas sensors
gas_pin_1 = 21  # Example GPIO pin for sensor 1
gas_pin_2 = 22  # Example GPIO pin for sensor 2

# DEFINE BUZZER
buzzer_pin = 23

# Define LED
led_pin = 24

# For pushbullet
config = configparser.ConfigParser()
config.read('config.ini')
access_token = config['Pushbullet']['API_KEY']
pb = Pushbullet(access_token)

# Define the GPIO pin connected to the flow sensor
FLOW_SENSOR_PIN = 14  # Change this according to your setup

# Variables to hold the flow sensor data
pulse_count = 0
flow_rate = 0.0
last_time = 0

# Function to read analog value from the sensor
def read_analog(pin):
    GPIO.setup(pin, GPIO.IN)
    analog_value = GPIO.input(pin)
    return analog_value

# Function to convert analog value to gas concentration (adjust based on your sensor)
def convert_to_concentration(sensor_value):
    # Your conversion logic here
    # Example: gas_concentration = (sensor_value / 1023.0) * 100.0
    return sensor_value

def pulse_counter(channel):
    global pulse_count
    pulse_count += 1

def calculate_flow_rate():
    global pulse_count, flow_rate, last_time
    current_time = time.time()
    if current_time - last_time >= 1:  # Calculate flow rate every 1 second
        flow_rate = pulse_count / 7.5  # 7.5 is the calibration factor for the flow sensor
        pulse_count = 0
        print("Flow Rate: {:.2f} L/min".format(flow_rate))
        last_time = current_time

def setup():
    GPIO.setup(FLOW_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(buzzer_pin, GPIO.OUT)  # Setup buzzer pin as an OUTPUT
    GPIO.setup(led_pin, GPIO.OUT)  # Setup LED pin as an OUTPUT
    GPIO.add_event_detect(FLOW_SENSOR_PIN, GPIO.FALLING, callback=pulse_counter)

def loop():
    try:
        while True:
            gas_concentration_1 = read_analog(gas_pin_1)
            gas_concentration_2 = read_analog(gas_pin_2)
            if gas_concentration_1 > 0 or gas_concentration_2 > 0:
                print("GAS LEAKAGE DETECTED")
                pb.push_note("GAS LEAKAGE DETECTED", "Gas leakage detected!")
                GPIO.output(buzzer_pin, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(buzzer_pin, GPIO.LOW)
            else:
                print("NO GAS LEAKAGE DETECTED")
            
            calculate_flow_rate()

            if flow_rate < 4.5:
                print("OIL LEAKAGE DETECTED")
                pb.push_note("OIL LEAKAGE DETECTED", "Oil leakage detected!")
                GPIO.output(led_pin, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(led_pin, GPIO.LOW)
            else:
                print("OIL LEAKAGE NOT DETECTED")
            time.sleep(2)  # Adjust this sleep time based on your requirements
    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
    setup()
    loop()
