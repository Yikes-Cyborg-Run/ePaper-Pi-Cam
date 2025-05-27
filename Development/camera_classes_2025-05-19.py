import time, datetime, os, logging, re
from gpiozero import LED, Button
from picamzero import Camera
from waveshare_epd import epd2in7_V2 # -- the 2.7inch GPIO HAT
from PIL import Image, ImageDraw, ImageFont

class Menu():
    def __init__(self):
        config=Config().load()
        self.epd=epd2in7_V2.EPD()
#        self.h=h; self.p=p; self.m=m; self.u=u; self.d=d; self.sel=sel
        self.image_dir="/home/pi/ePaper-Pi-Cam/photos/"
        self.font_dir="/home/pi/ePaper-Pi-Cam/Fonts"
        self.font_list=[] # for font menu
        for f in os.listdir(self.font_dir):
            if os.path.isfile:
                os.path.join(self.font_dir, f)
                self.font_list.append(f)

        self.font_size=int(config["fontsize"])
        self.font_path="/home/pi/ePaper-Pi-Cam/Fonts/"+config["font"]
        self.menu_list={
                "Main Menu":["Manual Scroll", "Camera", "Camera Options", "Time-lapse Camera", "Autoscroll", "Delete"],
                "Camera Options":["Font", "Font Size", "Display Rotation", "Autoscroll Duration", "Time-Lapse Duration", "White Balance", "Shut Down", "Delete All"],
                "White Balance":["auto", "tungsten", "fluorescent", "indoor", "daylight", "cloudy"],
                "Font Size":["14","18","20","22"],
                "Autoscroll Duration":["10", "30", "60", "120", "300", "600"],
                "Time-lapse Duration":["1", "30", "60", "300", "600", "1800", "3600"],
                "Display Rotation":["90", "180", "270"],
                "Timestamp Photo":["True", "False"],
                "Font": self.font_list,
                }
        self.ignore_list=["Camera", "Take Photo", "Time-lapse Camera", "Autoscroll", "Manual Scroll", "Delete", "Delete All"]

    def build(self, h, sel, photo_list):
        self.epd.init()
#        menu_list=self.menu_list
#        config=Config().load()
#        font_path="/home/pi/ePaper-Pi-Cam/Fonts/"+config["font"]
#        fontsize=int(config["fontsize"])
        use_menu=self.menu_list[sel]
        image=Image.new("1", (self.epd.height, self.epd.width), 255)
        draw=ImageDraw.Draw(image)
        font=ImageFont.truetype(self.font_path, self.font_size+4)
        draw.text((20,10),sel.upper(),font=font,fill=0)
        font=ImageFont.truetype(self.font_path, self.font_size)
        Log().log(f"{sel.upper()} -- {use_menu}" ,1)
        y=40
        highlighted=use_menu[h]
        for item in use_menu:
            item=str(item)
            if item=="Autoscroll" or item=="Manual Scroll" or item=="Delete" or item=="Delete All":
                show=item+f" - {len(photo_list)} photos"
            else:
                show=item
            if item==highlighted:
                show="-- "+show
            draw.text((20,y),show,font=font,fill=0)
            y+=20
        self.epd.display(self.epd.getbuffer(image))
        return

#    def select(self, h, sel, menu_list, ignore_list, p, m, u, d):
    def select(self, h, p, m, u, d, sel):
        use_menu=self.menu_list[sel]
        final_data=[h, sel, True]
        limit=len(use_menu)-1

        if sel not in self.ignore_list:
            if p.is_pressed:
                final_data=[0, use_menu[h], False]
                if sel in self.menu_list["Camera Options"]:
                    final_data=Config().save(sel, use_menu[h])
            elif m.is_pressed: # go to main menu
                final_data=[0, "Main Menu", False]
            elif u.is_pressed:
                h+=1
                if h>limit:h=0
                final_data=[h, sel, False]
            elif d.is_pressed:
                h-=1 
                if h<0:h=limit
                final_data=[h, sel, False]
        else: # no changes, return initial data
            final_data=[0, sel, True]
        return final_data

class Config():
    def __init__(self):
        self.config_path="/home/pi/ePaper-Pi-Cam/config.txt"
        self.epd=epd2in7_V2.EPD()

    def load(self):
#        Log().log("Loading config....",1)
        config={}
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as file:
                for line in file:
                    if "=" in line:
                        key, value=line.strip().split("=", 1)
                        config[key]=value
                        #Log.log(f"Loaded: {key} -- {value}",1)
#            Log().log("Loaded config.",1)
        else:
            Log().log("No config file.",1)
        return config

    def save(self, k, v):
#        epd=epd2in7_V2.EPD()
        self.epd.init()
        k=k.lower()
        k=re.sub(r'[^a-zA-Z0-9]', '', k)
        config=Config().load()
        config[k]=str(v)
        Log().log(f"Saving option....\n{k} - {v}",1)
        # Save updated config
        with open(self.config_path, 'w') as file:
            for key, value in config.items():
                file.write(f"{key}={value}\n")
            time.sleep(.5)
        Log().log("Saved config",1)
        return [0,"Camera Options",False]

class Warn():
    def __init__(self):
        self.epd=epd2in7_V2.EPD()
        self.config=Config().load()
        self.font_path="/home/pi/ePaper-Pi-Cam/Fonts/"+self.config["font"]
        self.fontsize=int(self.config["fontsize"])

    def warn(self, sel, photo_list, num):
#        config=Config().load()
#        font_path="/home/pi/ePaper-Pi-Cam/Fonts/"+config["font"]
#        fontsize=int(config["fontsize"])
        image=Image.new("1", (self.epd.height, self.epd.width), 255)
        draw=ImageDraw.Draw(image)
        font=ImageFont.truetype(self.font_path, self.fontsize+4)
        draw.text((20,10),sel.upper(),font=font,fill=0)
        if sel=="Camera":
            draw.text((20,50),"Camera Ready \nPress photo button.",font=font,fill=0)
            sel="Take Photos"

        elif sel=="Delete All Photos":
            draw.text((20,50),"No photos to show.",font=font,fill=0)
            print("Purge ALL Warning")
  #          sel="Purge Confirmed"

        elif sel=="Delete Single Photo":
            Log().log("Delete single photo warning...", 1)
            filename=photo_list[num]
            Log().log(f"Check delete: {filename}",1)
            image=Image.open(filename)
            image=image.resize((self.epd.height, self.epd.width))
 #           image=image.resize((50, 100))
            draw=ImageDraw.Draw(image)
            font=ImageFont.truetype(self.font_path, self.fontsize+4)
            draw.text((20,10), "Are you SURE you want to \ndelete this photo?", font=font, fill=0)
            font=ImageFont.truetype(self.font_path, self.fontsize)
            draw.text((20,10), "Press Menu button to cancel\nPress Photo button to delete", font=font, fill=0)

        self.epd.display(self.epd.getbuffer(image))
        # !!!!!!! KEY PRESS HERE TO SEND THE ACTION
        return [0, sel, True]

    def no_photos(self):
        Log().log("List selected, but no photos on file.", 0)
        LEDs.LEDs(0,0,1)
#        config=Config().load()
#        font_path="/home/pi/ePaper-Pi-Cam/Fonts/"+config["font"]
#        fontsize=int(config["fontsize"])
        image=Image.new("1", (self.epd.height, self.epd.width), 255)
        draw=ImageDraw.Draw(image)
        font=ImageFont.truetype(self.font_path, self.fontsize+4)
        draw.text((20,50),"No photos to show.",font=font,fill=0)
        font=ImageFont.truetype(self.font_path, self.fontsize)
        draw.text((20,100),"Press menu button.",font=font,fill=0)
        self.epd.display(self.epd.getbuffer(image))

class Action():
    def __init__(self):
        self.config=Config().load()
        self.timestamp_photo=self.config["timestampphoto"]
        self.epd=epd2in7_V2.EPD()
#        self.imiage_dir

    def take_photo(self, p, cam, photo_list, image_dir):
        if p.is_pressed:
            LEDs.LEDs(0,0,1)
#            timestamp_photo=config["timestampphoto"]
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # Get the current timestamp
            filename=f"{timestamp}.jpg" # Construct the filename
            if self.timestamp_photo==True: # Check if timestamping is enabled in config...
                cam.annotate(timestamp, 'plain-small', 'white', 1, 2, [5,170]) # add a timestamp to photo if it is
            cam.take_photo(image_dir+filename)
#            epd=epd2in7_V2.EPD()
#            epd.init()
            img_path=os.path.join(image_dir, filename)
            image=Image.open(img_path)
            image=image.resize((self.epd.height, self.epd.width))
            self.epd.display(self.epd.getbuffer(image)) # Display the final image
            LEDs.LEDs(1,0,0)
            photo_list.append(img_path)
        return photo_list

    def display_photo(self, photo_list, key):
        Log().log("Loading file...", 1)
        filename=photo_list[key]
        image=Image.open(filename)
        image=image.resize((self.epd.height, self.epd.width))
        self.epd.display(self.epd.getbuffer(image))
        Log().log("Displayed file: "+filename,1)
        return None
    
    def manual_scroll(u, d, photo_list, data):
        num=data[0]
        drawn=data[1]
        if len(photo_list)>0:
            limit=len(photo_list)-1
            if drawn==True:
                if u.is_pressed:
                    num+=1
                    if num>limit:num=0
                    return [num, False]
                elif d.is_pressed:
                    print("d")
                    num-=1
                    if num<0: num=limit
                    return [num, False]
                return [num, True]
            else:
                Action().display_photo(photo_list, num)
                return[num, True]
        else:
            Warn().no_photos()

    #!!!!!!! NEED TO check where some of these calculations are
    def autoscroll(self, photo_list):
        if len(photo_list)>0:
            if drawn==True:
                now_time=datetime.datetime.now()
                now=int(time.mktime(now_time.timetuple()))
                if now>future:
                    list_increment+=1
                    if list_increment>=len(photo_list)-1:
                        list_increment=0
                    Log().log("Autoscroll Increment: "+str(list_increment), 1)
                    display_photo(photo_list, list_increment)
                    future=Calc.future(self.config["autoscroll_duration"])
            else:
                Action().display_photo(self.epd, photo_list, list_increment)
                Calc.future(self.config["autoscroll_duration"])
        else:
            if drawn==False:
                drawn=True
                Warn().no_photos_msg()

class LEDs():
    def LEDs(green, yellow, red):
        LED_G=LED(20)
        LED_Y=LED(16)
        LED_R=LED(12)
        if green==1: LED_G.on()
        else:  LED_G.off()
        if yellow==1: LED_Y.on()
        else: LED_Y.off()
        if red==1: LED_R.on()
        else: LED_R.off()

class Calc():
    def future(autoscroll_duration):
        # Get the current timestamp
        now_time=datetime.datetime.now()
        now=int(time.mktime(now_time.timetuple()))
        # Add autoscroll_duration to timestamp
        future_time=now_time+datetime.timedelta(seconds=autoscroll_duration)
        future=int(time.mktime(future_time.timetuple()))
        # Print the original and updated timestamps
        Log().log("   NOW: "+str(now),1)
        Log().log("FUTURE: "+str(future),1)
        return future

    def timelapse_text():
        config=Config().load()
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

class Log():
    def __init__(self):
        pass
    def log(self, msg, err_type):
        err=["ERROR", "INFO", "DEBUG", "CRITICAL", "WARNING"]
        log_path="/home/pi/ePaper-Pi-Cam/log.log"
        logger=logging.getLogger(log_path)
        logging.basicConfig(filename=log_path, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%I:%M:%S %p',)
        err=err[err_type]
        print(err[err_type]+" : "+msg)
        if(err_type==0):logger.error(msg)
        elif(err_type==1):logger.info(msg)
        elif(err_type==2):logger.debug(msg)
        elif(err_type==3):logger.critical(msg)
        elif(err_type==4):logger.warning(msg)
