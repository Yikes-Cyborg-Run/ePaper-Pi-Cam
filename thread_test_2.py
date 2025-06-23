import threading
import time
import keyboard

class LEDs():
    def flash():
    #    f=keyboard.is_pressed('ctrl')
    #	if self.config['flash']=='Yes':
        f="Yes"
        if f=='Yes':
    #		LED_FLASH=LED(23)
            t=threading.current_thread()
            n=0
            while getattr(t, "do_run", True):
                n+=1
                # LED_FLASH.on()
                print (f"{n} ON ")
                time.sleep(1)
            # LED_FLASH.off()
        print("OFF")

def main():
    flash_LED=threading.Thread(target=LEDs.flash)
    flash_LED.start()
    print("Loop start")
    while True:
        time.sleep(2) ## SIMULATION CODE BLOCK
        flash_LED.do_run = False
        print("Done")

if __name__ == "__main__":
    main()

"""
import threading
import time

class MyStoppableThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.do_run = True # Initialize the flag to True

    def run(self):
        while self.do_run:
            print("Thread is running...")
            time.sleep(1)
        print("Thread stopped.")

# Create and start the thread
my_thread = MyStoppableThread()
my_thread.start()

# Let the thread run for a few seconds
time.sleep(3)

# Stop the thread by setting do_run to False
my_thread.do_run = False
my_thread.join() # Wait for the thread to finish
"""
