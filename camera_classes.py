import time, datetime, os, logging, sys, keyboard
from gpiozero import LED, Button
from picamzero import Camera
from waveshare_epd import epd2in7_V2 # -- the 2.7inch GPIO HAT
from PIL import Image, ImageDraw, ImageFont

class Menu():

    def build(h, selection, menu_list):
        use_menu=menu_list[selection]
        if selection=="Main Menu":
            go_back_to="Main Menu"
        if selection=="Camera Options":
            go_back_to="Main Menu"

        print(str(selection).upper())
        highlighted=use_menu[h]
        for item in use_menu:
            if item==highlighted:
                item=">"+item
            print (f"item: {item}")
        return

    def select(h, selection, menu_list, ignore_list):
        use_menu=menu_list[selection]
        final_data=[h,selection]
        limit=len(use_menu)-1
        
        if selection not in ignore_list:
            k=keyboard.read_key()
            time.sleep(0.2)
            print(f"pressed: {k}")
            if k:
                if k=="up":
                    h-=1 
                    if h<0:h=limit
                    final_data=[h, selection]
                if k=="down":
                    h+=1
                    if h>limit:h=0
                    final_data=[h, selection]
                if k=="enter":
                    final_data=[0, use_menu[h]]
                    if selection in menu_list["Camera Options"]:
                        option=selection.lower()
                        option.replace(" ", "_")
                        option.replace("-", "")
                        final_data=Config.save(option, use_menu[h])
                if k=="esc":
                    final_data=[0,"Main Menu"]

        else:
            final_data=[0,selection]

        return final_data

class Config():
    def __init__(self):
        pass

    def load():
        config_path=r"C:/Users/ckingsbury/OneDrive - City of Port Orange/Desktop/ePaper-Pi-Cam/config.txt"
        config={}
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                for line in file:
                    if "=" in line:
                        key, value=line.strip().split("=", 1)
                        config[key]=value
                        print(f" loaded: {key} -- {value}")
            print("Loaded config.")
        else:
            print("No config file.")
        return config

    def save(passed_key, passed_value):
        config=Config.load()
        config[passed_key]=passed_value
        config_path=r"C:/Users/ckingsbury/OneDrive - City of Port Orange/Desktop/ePaper-Pi-Cam/config.txt"
        print(f"Saving options....\n{passed_key} - {passed_value}")
        # Save updated config
        with open(config_path, 'w') as file:
            for key, value in config.items():
                file.write(f"{key}={value}\n")
            print("Saved!")
            time.sleep(.5)
        print("Options saved")
        return [0,"Camera Options"]

class Warn():
    def warn(selection):
        if selection=="Camera":
            print("Camera Message")
            selection="Take Photos"

        elif selection=="Delete Single Photo":
            print("Delete Warning")
            selection = "Purge Confirmed"

        elif selection=="Delete All Photos":
            print("Delete Warning")
            selection="Purge Confirmed"

        # !!!!!!! KEY PRESS HERE TO SEND THE ACTION
        return [0, selection]

    def no_photos():
        global head_fs, base_fs
        log("List selected, but no photos on file.", 0)
        LEDs(0,0,1)
        image=Image.new("1", (epd.height, epd.width), 255)
        draw=ImageDraw.Draw(image)
        font=ImageFont.truetype(font_path, head_fs)
        draw.text((20,50),"No photos to show.",font=font,fill=0)
        font=ImageFont.truetype(font_path, base_fs)
        draw.text((20,100),"Press menu button.",font=font,fill=0)
        epd.display(epd.getbuffer(image))
            


        k=keyboard.read_key()
        if k:
            if k=="enter":
                return [0, selection]
            elif k=="esc":
                return [0, "Main Menu"]

class Action():
    def act(selection):
        print(f"Action: {selection}")

    def take_photo(photo_list, image_folder, timestamp_photo):
        LEDs.LEDs(0,0,1)
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # Get the current timestamp
        filename=f"{timestamp}.jpg" # Construct the filename
        if timestamp_photo==True: # Check if timestamping is enabled in config...
            cam.annotate(timestamp, 'plain-small', 'white', 1, 2, [5,170]) # add a timestamp to photo if it is
        cam.take_photo(image_folder+filename)
        img_path=os.path.join(image_folder, filename)
        image=Image.open(img_path)
        image=image.resize((epd.height, epd.width))
        epd.display(epd.getbuffer(image)) # Display the final image
        LEDs.LEDs(1,0,0)
        photo_list.append(img_path)
        return [0,"Take Photos",photo_list]

    def display_photo(photo_list, key):
        global head_fs, base_fs
        log("Loading file...", 1)
        filename=photo_list[key]
        image=Image.open(filename)
        image=image.resize((epd.height, epd.width))
        epd.display(epd.getbuffer(image))
        log("Displayed file: "+filename,1)
        return None
    
    def manual_scroll(photo_list, photo_increment):
        if(len(photo_list)>0):
            k=keyboard.key_pressed()
            limit=len(photo_list)-1
            if k:
                if k=="up":
                    photo_increment+=1
                    if(photo_increment>=limit):photo_increment=0
                if k=='down':
                    photo_increment+=1
                    if(photo_increment>=limit):photo_increment=0
                Action.display_photo(photo_increment)
        else:
            Warning.no_photos()
        return photo_increment
    

    



class LEDs():
    def LEDs(green,yellow,red):
        if green==1: LED_G.on()
        else:  LED_G.off()
        if yellow==1: LED_Y.on()
        else: LED_Y.off()
        if red==1: LED_R.on()
        else: LED_R.off()

class Calc():
    def future():
        global now_time, now, future_time, future, drawn, autoscroll_duration
        # Get the current timestamp
        now_time=datetime.datetime.now()
        now=int(time.mktime(now_time.timetuple()))
        # Add autoscroll_duration to timestamp
        future_time=now_time+datetime.timedelta(seconds=autoscroll_duration)
        future=int(time.mktime(future_time.timetuple()))
        # Print the original and updated timestamps
        Log.log("   NOW: "+str(now),1)
        Log.log("FUTURE: "+str(future),1)
        drawn=True
        return None

    def timelapse_text():
        config=Config.load()
        dur=config["timelapse_duration"]
        if(dur<60):
            suffix="second"
            dur=dur
        elif(dur>60 and dur<3600):
            suffix="minute"
            dur=dur/60
        elif(dur>60 and dur<3600):
            suffix="hour"
            dur=dur/3600
        # format the text to display
        if dur!=1:
            final=str(dur)+" "+suffix+"s"
        else:
            final=suffix
        return final
