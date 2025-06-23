Okay, here's a Python script that uses threading to turn an LED on while a main process runs, and then turns it off after 2 seconds using the threading.Timer class. 
Important Notes:
GPIO Library: This code assumes you're using a library like gpiozero for controlling GPIO pins (common on Raspberry Pi). You'll need to adapt it if you're using a different method.
GPIO Pin: Replace 17 with the actual GPIO pin number your LED is connected to.
Permissions: You might need to run the script with sudo or equivalent privileges to access GPIO pins. 
python
import threading  # For creating threads and timers
import time  # For simulating work
from gpiozero import LED  # To control the LED

# Define the GPIO pin connected to the LED
LED_PIN = 17  # Replace with your LED pin
led = LED(LED_PIN)  # Create an LED object

def turn_off_led():
    """Function to turn off the LED."""
    print("Turning LED off...")
    led.off()  # Turn off the LED

def main_process():
    """Simulates the main process that takes some time."""
    print("Main process started.")
    # Simulate some work being done by the main process
    time.sleep(5)  # Replace with your actual process logic
    print("Main process finished.")

# Turn the LED on
print("Turning LED on...")
led.on()  # Turn on the LED

# Create a Timer thread to turn off the LED after 2 seconds
timer = threading.Timer(2.0, turn_off_led)  # Create a timer that calls turn_off_led after 2 seconds
timer.start()  # Start the timer thread

# Run the main process
main_process()  # The main process runs concurrently with the timer

# Wait for the timer thread to finish (optional, but good practice)
timer.join()  # Wait for the timer to complete its task

# Clean up GPIO pins (gpiozero does this automatically)
# If using RPi.GPIO, you would need GPIO.cleanup() here
Explanation:
Import necessary modules: threading for managing threads and timers, time for delays, and gpiozero for controlling the LED.
Define LED pin and object: LED_PIN is set to the GPIO pin number, and an LED object is created to control it.
turn_off_led() function: This function simply turns the LED off and prints a message.
main_process() function: This function simulates the main task your script performs. Here, it just waits for 5 seconds. Replace this with your actual process logic.
Turn LED on: The LED is immediately turned on using led.on().
Create and start Timer:
A threading.Timer object is created.
The first argument (2.0) is the delay in seconds before the timer's function is executed.
The second argument (turn_off_led) is the function to be called after the delay.
timer.start() starts the timer thread, which will wait for 2 seconds and then execute turn_off_led().
Run main process: The main_process() function is called, which runs concurrently with the timer thread.
Join Timer (optional): timer.join() ensures the main program waits for the timer thread to complete before exiting. 
This approach allows your main process to continue running while the LED is on, and the timer thread handles turning it off after the specified duration. 
