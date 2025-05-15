import time

class Btn:
    def __init__():
        pass

    def up(current, state):
        if(state==1):
            current+=1
        return current

    def down(current, state):
        if(state==1):
            current-=1
        return current

    def select(current, menu_items):
        return menu_items[current]

current=0
menu_items=["q","w","e","r","t","y"]

state=1
current=Btn.up(current, state)

b=Btn.select(current, menu_items)
print(b)




"""
try:
    while True:
        current=Btn.up(current)
        print(current)
        time.sleep(1)
except: 
    print("oop")
"""