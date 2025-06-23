import threading
import time

def doit():
    t=threading.current_thread()
    n=0
    while getattr(t, "do_run", True):
        n+=1
        print (f"{n} working ")
        time.sleep(1)
    print("Stopping as you wish.")

def main():
    t=threading.Thread(target=doit)
    t.start()
    time.sleep(2) ## SIMULATION CODE BLOCK
    t.do_run = False

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
