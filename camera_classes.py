import time, datetime, os, logging, re
from gpiozero import LED, Button
from picamzero import Camera
from waveshare_epd import epd2in7_V2 # -- the 2.7inch GPIO HAT
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Class to build, navigate through, and select menus
class Menu():
    def __init__(self):
        self.config=Config().load()
        self.epd=epd2in7_V2.EPD()
        self.home_dir=Path(__file__).parent.resolve() # Current directory
        self.image_dir=self.home_dir / 'Photos'
        self.font_dir=self.home_dir / 'Fonts'
        self.font_list=[] # for font menu
        for f in os.listdir(self.font_dir):
            if os.path.isfile:
                os.path.join(self.font_dir, f)
                self.font_list.append(f)
        self.font_size=int(self.config['fontsize'])
        self.font_path=self.home_dir / 'Fonts' / self.config['font']
        self.menu_list={
                # Camera options to vflip, hflip, greyscale
                'Main Menu':['Manual Scroll', 'Camera', 'Display Options', 'Camera Options', 'Time-lapse Camera', 'Autoscroll', 'Delete All'],
                'Camera Options':['Time-Lapse Duration', 'White Balance', 'Shut Down', 'Contrast', 'Exposure'],
                'White Balance':['Auto', 'Cloudy', 'Daylight', 'Fluorescent', 'Indoor', 'Tungsten'],
                'Time-lapse Duration':['1', '30', '60', '300', '600', '1800', '3600'],
                'Timestamp Photo':['Yes', 'No'],
                'Exposure':['None', '5', '10', '30', '60', '120'],
                'Contrast':['0', '5', '10', '15', '20', '25', '32'],
                
                'Display Options':['Font', 'Font Size', 'Display Rotation', 'Autoscroll Duration', 'Show Splash Screen'],
                'Font Size':['12', '14', '18', '20', '22'],
                'Autoscroll Duration':['10', '30', '60', '120', '300', '600'],
                'Display Rotation':['90', '180', '270'],
                'Show Splash Screen':['Yes', 'No'],
                'Font': self.font_list,
                }
        # These do not need a menu created
        self.ignore_list=['Camera', 'Take Photo', 'Time-lapse Camera', 'Autoscroll', 'Manual Scroll', 'Delete', 'Delete All']

    # Build the selected menu
    # Take sel = selected menu to use, h = item that's highlighted, photo_list = to tally the total photos 
    def build(self, h, sel, photo_list):
        self.epd.init()
        use_menu=self.menu_list[sel]
        image=Image.new('1', (self.epd.height, self.epd.width), 255)
        draw=ImageDraw.Draw(image)
        font=ImageFont.truetype(self.font_path, self.font_size+4)
        draw.text((20, 10), sel.upper(), font=font, fill=0)
        font=ImageFont.truetype(self.font_path, self.font_size)
        Log().log(f"{sel.upper()} -- {use_menu}" ,1)
        y=40
        highlighted=use_menu[h]
        for item in use_menu:
            item=str(item)
            # Show the total number of photos for these items
            if item=='Autoscroll' or item=='Manual Scroll' or item=='Delete' or item=='Delete All':
                show=item+f' - {str(len(photo_list))} photos'
            else:
                show=item
            if item==highlighted:
                show='-- '+show # add a mark to the one that's highlighted
            draw.text((20, y), show, font=font, fill=0)
            y+=20
        self.epd.display(self.epd.getbuffer(image))
        return

#    def navigate(self, h, sel, menu_list, ignore_list, p, m, u, d):
    # Function to navigate through the menu
    # h = highlighted item, p = photo button, m = menu button, u = up button, d = down button
    # sel = selected item that is returned when p is pressed to build the menu
    def navigate(self, h, p, m, u, d, sel):
        use_menu=self.menu_list[sel]
        data=[h, sel, True]
        limit=len(use_menu)-1
        if sel not in self.ignore_list:
            if p.is_pressed:
                data=[0, use_menu[h], False]
                if (sel in self.menu_list['Camera Options']) or (sel in self.menu_list['Display Options']):
                    data=Config().save(sel, use_menu[h])
            elif m.is_pressed: # go to main menu
                data=[0, 'Main Menu', False]
            elif u.is_pressed:
                h+=1
                if h>limit:h=0
                data=[h, sel, False]
            elif d.is_pressed:
                h-=1 
                if h<0:h=limit
                data=[h, sel, False]
        else: # No changes, return initial data
            data=[0, sel, True]
        return data

# Class to display warnings/notices that prompt the user for a button press
class Warn():
    def __init__(self):
        self.epd=epd2in7_V2.EPD()
        self.config=Config().load()
        self.home_dir=Path(__file__).parent.resolve() # Current directory
        self.font_path= self.home_dir / self.config['font']
        self.fontsize=int(self.config['fontsize'])

    def warn(self, p, sel, num, data, photo_list):
        image=Image.new('1', (self.epd.height, self.epd.width), 255)
        draw=ImageDraw.Draw(image)
        font=ImageFont.truetype(self.font_path, self.fontsize+4)
        draw.text((20, 10), sel.upper(), font=font, fill=0)
        drawn=data[1]

        if sel=='Camera':
            draw.text((20, 50), "Camera Ready \nPress photo button.", font=font, fill=0)
            sel='Take Photos'

        elif sel=='Delete All':
            if photo_list>0:
                if p.is_pressed:
                    return[0, 'Purge Confirmed', False]
                elif drawn==False:
                    Log.log('Purge ALL Warning', 4)
                    draw.text((20, 10), f"Are you SURE you want to \ndelete ALL \n{str(len(photo_list))} photos on file?", font=font, fill=0)
                    font=ImageFont.truetype(self.font_path, self.fontsize)
                    draw.text((20, 10), "Press Menu button to cancel\nPress Photo button to confirm", font=font, fill=0)
                    data=[0, sel, True]
            else:
                Warn().no_photos()
                data=[0, 'Delete All', True]

        elif sel=='Delete Single Photo':
            Log().log("Delete single photo warning...", 1)
            filename=photo_list[num]
            Log().log(f"Check delete: {filename}", 1)
            image=Image.open(filename)
            image=image.resize((self.epd.height, self.epd.width))
 #           image=image.resize((50, 100))
            draw=ImageDraw.Draw(image)
            font=ImageFont.truetype(self.font_path, self.fontsize+4)
            draw.text((20, 10), "Are you SURE you want to \ndelete this photo?", font=font, fill=0)
            font=ImageFont.truetype(self.font_path, self.fontsize)
            draw.text((20, 10), "Press Menu button to cancel\nPress Photo button to delete", font=font, fill=0)

        self.epd.display(self.epd.getbuffer(image))
#        return [0, sel, True] # NO CHANGE
        return data

    def no_photos(self):
        Log().log("List selected, but no photos on file.", 0)
        LEDs.LEDs(0, 0, 1)
        image=Image.new('1', (self.epd.height, self.epd.width), 255)
        draw=ImageDraw.Draw(image)
        font=ImageFont.truetype(self.font_path, self.fontsize+4)
        draw.text((20, 50), "No photos to show.", font=font, fill=0)
        font=ImageFont.truetype(self.font_path, self.fontsize)
        draw.text((20, 100), "Press menu button.", font=font, fill=0)
        self.epd.display(self.epd.getbuffer(image))

class Action():
    def __init__(self):
        self.home_dir=Path(__file__).parent.resolve() # Current directory
        self.config=Config().load()
        self.epd=epd2in7_V2.EPD()
        self.timestamp_photo=self.config['timestampphoto']
        self.image_dir=self.home_dir / 'Photos'
        self.font_path=self.home_dir / 'Fonts' / self.config['font']

    # p: photo button pressed, cam: initialized camera object from main(), existing photo_list
    def take_photo(self, p, cam, photo_list):
        if p.is_pressed:
            LEDs.LEDs(0, 0, 1)
            timestamp=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') # Get the current timestamp
            filename=f'{timestamp}.jpg' # Construct the filename
            if self.timestamp_photo==True: # Check if timestamping is enabled in config...
                cam.annotate(timestamp, 'plain-small', 'white', 1, 2, [5, 170]) # add a timestamp to photo
            cam.take_photo(self.image_dir+filename)
            img_path=os.path.join(self.image_dir, filename)
            image=Image.open(img_path)
            image=image.resize((self.epd.height, self.epd.width))
            self.epd.display(self.epd.getbuffer(image)) # Display the final image
            LEDs.LEDs(1, 0, 0)
            photo_list.append(img_path)
        return photo_list

    def display_photo(self, photo):
        Log().log("Loading file...", 1)
        image=Image.open(photo)
        image=image.resize((self.epd.height, self.epd.width))
        self.epd.display(self.epd.getbuffer(image))
        Log().log(f"Displayed file: {photo}",1)
        return None
    
    # MANUAL SCROLL
    # Tab through existing photos with u: up button, d: down button
    # Also uses: existing photo_list and data:[photo_increment, drawn - True or False]
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
                    print('d')
                    num-=1
                    if num<0: num=limit
                    return [num, False]
                return [num, True]
            else:
                Action().display_photo(photo_list[num])
                return[num, True]
        else:
            Warn().no_photos()

    # AUTOSCROLL
    # Eses existing photo_list and starts at num=0
    # Uses autoscrollduration from config.txt, calculates future time to change photo
    # !!!!!!! NEED TO check where some of these calculations are
    def autoscroll(self, photo_list, data):
        num=data[0]
        drawn=data[1]
        future=data[2]
        if len(photo_list)>0:
            if drawn==True:
                now_time=datetime.datetime.now()
                now=int(time.mktime(now_time.timetuple()))
                if now>future: 
                    num+=1
                    if num>=len(photo_list)-1: num=0
                    Log().log("Autoscroll Increment: "+str(num), 1)
                    Action.display_photo(photo_list[num])
                    future=Calc.future(self.config['autoscroll_duration'])
                    data=[num, False, future]
            else:
                Action().display_photo(photo_list[num])
                future=Calc.future(self.config['autoscroll_duration'])
                data=[num, True, future]
        else:
            if drawn==False:
                Warn().no_photos()
                data=[0, True, future] ## ??????? set to tru or false? 
        return data        

    # Function to delete ALL photos on file
    # I used the word "PURGE" to make it stand out against the word delete.
    def purge_photo_dir(self):
        Log.log("Attempting to purge all photos...",1)
        num=len(self.image_dir)
        for file in self.image_dir.iterdir():
            if file.is_file():
                file.unlink()
                Log.log(f"Deleted: {file}")
        Log.log(f"Deleted All {num} photos")
        image=Image.new('1', (self.epd.height, self.epd.width), 255)
        draw=ImageDraw.Draw(image)
        font=ImageFont.truetype(self.font_path, self.fontsize+4)
        draw.text((20, 50), f"Deleted All {num} photos", font=font, fill=0)
        font=ImageFont.truetype(self.font_path, self.fontsize)
        draw.text((20, 100), "Opening Main Menu....", font=font, fill=0)
        self.epd.display(self.epd.getbuffer(image))
        time.sleep(3)
        return [0, "Main Menu", False]

        """
        for filename in os.listdir(self.image_dir):
            file_path=os.path.join(self.image_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutilrmtree(file_path)
            except Exception as e:
                Log.log("Failed to delete", 0)
        """
                
# Light up LEDs
# Takes 0 or 1, 0=off, 1=on
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
    # Calculates a future time to reset next picture in Autoscroll
    def future(autoscroll_duration):
        now_time=datetime.datetime.now() # Get the current datetime
        now=int(time.mktime(now_time.timetuple())) # Make timestamp
        future_time=now_time+datetime.timedelta(seconds=autoscroll_duration) # Add autoscroll_duration to timestamp
        future=int(time.mktime(future_time.timetuple()))
        # Log the current and future timestamps
        Log().log("   NOW: "+str(now),1)
        Log().log("FUTURE: "+str(future),1)
        return future

    # Display the current timelapse setting
    # !!!!!!! IN PROGRESS
    def timelapse_text():
        config=Config().load()
        dur=config['timelapse_duration']
        if(dur<60):
            suffix='second'
            dur=dur
        elif(dur>60 and dur<3600):
            suffix='minute'
            dur=dur/60
        elif(dur>60 and dur<3600):
            suffix='hour'
            dur=dur/3600
        # format the text to display
        if dur!=1:
            final=str(dur)+' '+suffix+'s'
        else:
            final=suffix
        return final

class Config():
    def __init__(self):
        self.home_dir=Path(__file__).parent.resolve() # Current directory
        self.config_path=self.home_dir / 'config.txt'
        self.epd=epd2in7_V2.EPD()

    # Load config settings from txt file
    def load(self):
        config={}
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as file:
                for line in file:
                    if '=' in line:
                        key, value=line.strip().split('=', 1)
                        config[key]=value
            Log().log("Loaded config.", 1)
        else:
            Log().log("No config file.", 0)
        return config

    # Save config settings to txt file
    def save(self, k, v):
        self.epd.init()
        # Using key names from the Camera Options menu, strip down and make all lowercase
        k=k.lower(re.sub(r'[^a-zA-Z0-9]', '', k))
#        k=re.sub(r'[^a-zA-Z0-9]', '', k)
        config=Config().load()
        config[k]=str(v) # Assign passed variable to item
        Log().log(f"Saving option....\n{k} - {v}", 1)
        # Open txt file and save the updated config
        with open(self.config_path, 'w') as file:
            for key, value in config.items():
                file.write(f'{key}={value}\n')
            time.sleep(.5)
        Log().log("Saved config", 1)
        return [0, 'Camera Options', False]

# Save info to a log file
class Log():
    def __init__(self): # ??????? NEED ???????
        pass
    def log(self, msg, err_type):
        err=['ERROR', 'INFO', 'DEBUG', 'CRITICAL', 'WARNING']
        log_path='/home/pi/ePaper-Pi-Cam/log.log'
        logger=logging.getLogger(log_path)
        logging.basicConfig(filename=log_path, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%I:%M:%S %p',)
        err=err[err_type]
        print(err[err_type]+' : '+msg)
        if(err_type==0):logger.error(msg)
        elif(err_type==1):logger.info(msg)
        elif(err_type==2):logger.debug(msg)
        elif(err_type==3):logger.critical(msg)
        elif(err_type==4):logger.warning(msg)
