import time, datetime, os, logging, re, keyboard
from gpiozero import LED, Button
from picamzero import Camera
from waveshare_epd import epd2in7_V2 # -- the 2.7inch GPIO HAT
from PIL import Image, ImageDraw, ImageFont

class Menu():
    def build(h, epd, selection, menu_list, photo_list):
        config=Config.load()
        font_path="/home/pi/ePaper-Pi-Cam/Fonts/"+config["font"]
        fontsize=int(config["fontsize"])
        use_menu=menu_list[selection]
        image=Image.new("1", (epd.height, epd.width), 255)
        draw=ImageDraw.Draw(image)
        font=ImageFont.truetype(font_path, fontsize+4)
        draw.text((20,10),selection.upper(),font=font,fill=0)
        font=ImageFont.truetype(font_path, fontsize)
        Log.log(f"{selection.upper()} -- {use_menu}" ,1)
        y=40
        highlighted=use_menu[h]
        for item in use_menu:
            item=str(item)
            if item=="Autoscroll" or item =="Manual Scroll":
                show=item+f" - {len(photo_list)} photos"
            else:
                show=item
            if item==highlighted:
                show="-- "+show
            draw.text((20,y),show,font=font,fill=0)
            y+=20
        epd.display(epd.getbuffer(image))
        return

    def select(h, selection, menu_list, ignore_list, p, m, u, d):
        use_menu=menu_list[selection]
        final_data=[h,selection,True]
        limit=len(use_menu)-1

        if selection not in ignore_list:
            if p.is_pressed:
                final_data=[0, use_menu[h],False]
                if selection in menu_list["Camera Options"]:
                    final_data=Config.save(selection, use_menu[h])
            elif m.is_pressed:
                final_data=[0,"Main Menu", False]
            elif u.is_pressed:
                h+=1
                if h>limit:h=0
                final_data=[h, selection,False]
            elif d.is_pressed:
                h-=1 
                if h<0:h=limit
                final_data=[h, selection,False]
        else:
            final_data=[0,selection,True]
        return final_data

class Config():
    def load():
        Log.log(f"Loading config....",1)
        config_path=r"/home/pi/ePaper-Pi-Cam/config.txt"
        config={}
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                for line in file:
                    if "=" in line:
                        key, value=line.strip().split("=", 1)
                        config[key]=value
                        #Log.log(f"Loaded: {key} -- {value}",1)
            Log.log("Loaded config.",1)
        else:
            Log.log("No config file.",1)
        return config

    def save(k, v):
        epd=epd2in7_V2.EPD()
        epd.init()
        k=k.lower()
        k=re.sub(r'[^a-zA-Z0-9]', '', k)
        config=Config.load()
        config[k]=str(v)
        config_path=r"/home/pi/ePaper-Pi-Cam/config.txt"
        Log.log(f"Saving options....\n{k} - {v}",1)
        # Save updated config
        with open(config_path, 'w') as file:
            for key, value in config.items():
                file.write(f"{key}={value}\n")
            time.sleep(.5)
        Log.log("Saved config",1)
        return [0,"Camera Options",False]

class Warn():
    def warn(epd, selection, photo_list, num):
        config=Config.load()
        font_path="/home/pi/ePaper-Pi-Cam/Fonts/"+config["font"]
        fontsize=int(config["fontsize"])

        image=Image.new("1", (epd.height, epd.width), 255)
        draw=ImageDraw.Draw(image)
        font=ImageFont.truetype(font_path, fontsize+4)
        draw.text((20,10),selection.upper(),font=font,fill=0)

        if selection=="Camera":
            draw.text((20,50),"Camera Ready \nPress photo button.",font=font,fill=0)
            selection="Take Photos"

        elif selection=="Delete All Photos":
            draw.text((20,50),"No photos to show.",font=font,fill=0)
            print("Purge ALL Warning")
  #          selection="Purge Confirmed"

        elif selection=="Delete Single Photo":
            Log.log("Delete single photo warning...", 1)
            filename=photo_list[num]
            Log.log(f"Check delete: {filename}",1)
            image=Image.open(filename)
            image=image.resize((epd.height, epd.width))
 #           image=image.resize((50, 100))
            draw=ImageDraw.Draw(image)
            font=ImageFont.truetype(font_path, fontsize+4)
            draw.text((20,10), "Are you SURE you want to \ndelete this photo?", font=font, fill=0)
            font=ImageFont.truetype(font_path, fontsize)
            draw.text((20,10), "Press Menu button to cancel\nPress Photo button to delete", font=font, fill=0)

        epd.display(epd.getbuffer(image))
        # !!!!!!! KEY PRESS HERE TO SEND THE ACTION
        return [0, selection, True]

    def no_photos(epd):
        Log.log("List selected, but no photos on file.", 0)
        LEDs.LEDs(0,0,1)
        config=Config.load()
        font_path="/home/pi/ePaper-Pi-Cam/Fonts/"+config["font"]
        fontsize=int(config["fontsize"])
        image=Image.new("1", (epd.height, epd.width), 255)
        draw=ImageDraw.Draw(image)
        font=ImageFont.truetype(font_path, fontsize+4)
        draw.text((20,50),"No photos to show.",font=font,fill=0)
        font=ImageFont.truetype(font_path, fontsize)
        draw.text((20,100),"Press menu button.",font=font,fill=0)
        epd.display(epd.getbuffer(image))

class Action():
    def act(selection):
        Log.log(f"Action: {selection}",0)

    def take_photo(p, cam, epd, photo_list, image_folder):
        if p.is_pressed:
            LEDs.LEDs(0,0,1)
            config=Config.load()
            timestamp_photo=config["timestampphoto"]
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # Get the current timestamp
            filename=f"{timestamp}.jpg" # Construct the filename
            if timestamp_photo==True: # Check if timestamping is enabled in config...
                cam.annotate(timestamp, 'plain-small', 'white', 1, 2, [5,170]) # add a timestamp to photo if it is
            cam.take_photo(image_folder+filename)
#            epd=epd2in7_V2.EPD()
#            epd.init()
            img_path=os.path.join(image_folder, filename)
            image=Image.open(img_path)
            image=image.resize((epd.height, epd.width))
            epd.display(epd.getbuffer(image)) # Display the final image
            LEDs.LEDs(1,0,0)
            photo_list.append(img_path)
        return photo_list

    def display_photo(epd, photo_list, key):
        global head_fs, base_fs
        Log.log("Loading file...", 1)
        filename=photo_list[key]
        image=Image.open(filename)
        image=image.resize((epd.height, epd.width))
        epd.display(epd.getbuffer(image))
        Log.log("Displayed file: "+filename,1)
        return None
    
    def manual_scroll(u, d, epd, photo_list, data):
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
                Action.display_photo(epd, photo_list, num)
                return[num, True]
        else:
            Warn.no_photos(epd)

    def autoscroll(epd, photo_list, autoscroll_duration):
        if len(photo_list)>0:
            if drawn==True:
                now_time=datetime.datetime.now()
                now=int(time.mktime(now_time.timetuple()))
                if now>future:
                    list_increment+=1
                    if list_increment>=len(photo_list)-1:
                        list_increment=0
                    Log.log("Autoscroll Increment: "+str(list_increment), 1)
                    display_photo(epd, photo_list, list_increment)
                    Calc.future(autoscroll_duration)
            else:
                Action.display_photo(epd, photo_list, list_increment)
                Calc.future(autoscroll_duration)
        else:
            if drawn==False:
                drawn=True
                no_photos_msg()

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
        Log.log("   NOW: "+str(now),1)
        Log.log("FUTURE: "+str(future),1)
        return future

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

class Log():
    def log(msg, err_type):
        log_path="/home/pi/ePaper-Pi-Cam/log.log"
        logger=logging.getLogger(log_path)
        logging.basicConfig(filename=log_path, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%I:%M:%S %p',)
        err=["ERROR", "INFO", "DEBUG", "CRITICAL", "WARNING"]
        print(err[err_type]+" : "+msg)
        if(err_type==0):logger.error(msg)
        elif(err_type==1):logger.info(msg)
        elif(err_type==2):logger.debug(msg)
        elif(err_type==3):logger.critical(msg)
        elif(err_type==4):logger.warning(msg)
