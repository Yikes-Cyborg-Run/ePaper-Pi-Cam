<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/title.jpg' align='left'>  
<br>  

## A Raspberry Pi Camera to show photos on an ePaper display. ##  

### Table of Contents ###
• [Main Features](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam#main-features)
• [Introduction](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam#introduction)
• [Hardware](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam#hardware)
• [Install Raspberry Pi OS](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam#install-the-raspberry-pi-operating-system)
• [Install Modules](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam#install-modules)  
• [Enable SPI](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam#enable-spi)
• [Resources & To-Do](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam?#project-resources--notes-for-future-updatesto-do)


<!-- <img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/splash_lego_enclosure.jpg' align='right' width='550'>  -->
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/splash_lego_enclosure.jpg' width='650'>

_An early prototype of the ePaper-Pi-Cam. Please forgive the crude lego enclosure, I've no 3D printer!_  
<br>

# Main Features #
1) Use your camera to take photos and render them on-the-fly with an ePaper display.
2) Take timelapse photos with user-defined duration.
3) Display photos you've taken on Autoscroll function with a user-defined duration.
4) Manually scroll through photos you've taken and delete photos if you wish to.
5) Archive your Photos directory to a zip file for protecting or downloading later.
6) Purge all photos.
7) Customizable Camera Options: Display Font, Font Size, Time-Lapse Duration, Autoscroll Duration, Brightness, Contrast, Enable/Disable Flash, White Balance, Archive Photos, Show Splash Screen, Clear Display and Shut Down, Show Photo and Shut Down, Purge Photo Directory.

| Menu Name | Options/Items | 
|------------|------------|  
| Main | Camera, Time-Lapse, Manual Scroll, Autoscroll,  Camera Options, Display Options, System Options |  
| Camera Options | Brightness, Contrast, Flash, Time-Lapse Duration, White Balance |
| Display Options | Font, Font Size, Autoscroll Duration |
| System Options | Archive Photos, Show Splash Screen, Timestamp Photo, Clear Display and Shut Down,  Show Photo and Shut Down, Purge All Photos |

# Introduction #  
<table style="width:500px; border-collapse: collapse; padding: 0px;" align='right'>
<tr><td>
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/TL_sunset.gif'>
</td></tr>
<tr><td><i>This is a time-lapse compilation of the sun going down <br>from my porch. I put it together with photos I downloaded <br>from the camera taken at a 30-second interval.</i>
</td></tr>
</table>  

There are an increasing number of projects that take advantage of the ePaper display's functionality. I'm really drawn to these displays and the soft aesthetic they add to pretty much any project. There are many people who use the ePaper displays as a picture frame and I've always thought these were interesting. The Pi serves up photos and scrolls through them at an interval; simple enough but still very cool. So I thought, why not build an actual camera that takes photos and uses an ePaper display as the screen? I Googled around and didn't find anything of the sort -- a combination of a camera AND scrolling picture frame. So I decided to see if I could build one.  

Some may wonder, why use an ePaper display as a camera screen? Isn't it laggy with the re-drawing? The answer is yes, the screen does need to re-draw. This was one of my major hurdles in putting this together. The ePaper display will need to refresh each time there is a change to the image. With a normal display, the refresh rate is so fast, it's not even noticible. And with looping code, it's pretty much a non-issue in my opinion. But with ePaper, the refresh is very noticible. So I needed a way to let the program know that the screen had drawn and to not continue to refresh it upon each iteration of the program loop. I believe I did this in the most efficient way I know. But I certainly have plans to refine the code to have the display only partially refresh the changed areas.    
  
Just a couple of other quick notes: I understand full well that a lot of this code could be better, and some of it is likely downright offensive to a long-time Python programmer. For that I sincerely apologize. For example.... Classes. This project was originally an effort to force myself to gain a better understanding of Classes. Throughout my career, I've had little need to create or write them into any of my own code, other than have an understanding of them in plugins, ets. I've also had no experience in creating a decent-sized python app with the textbook structure for a properly organized app. I am aware this is not structured anywhere near properly, but I plan to make it better. Up until a little while ago I've never tried to put together a Github repo. Still, I think I'm learning and getting a little bit better; and that continuing to work on this will help me to improve on all of my shortcomings.  
  
To conclude, I would like to say that I would never offer anything up to the public that didn't work for me personally. At this point, I've gone though these steps a number of times from scratch. I know what some of the possible stumbling blocks might be, and hopefully I've doucumented how to overcome them in the walk-through. But if anyone has any issues, I will do my absolute best to help. And I am always open to suggestions to make this better and to hopefully learn even more myself.  

Enjoy!
<br>


# Hardware #  
**Hardware used in this project:**
1) Raspberry Pi Zero2 W
2) Waveshare 2.7-inch ePaper Hat (with built-in GPIO buttons)
3) Official Raspberry Pi Camera Module V2
4) Micro SD Card
5) Micro USB data cable → **$${\color{red}MAKE \space SURE \space IT'S \space A \space DATA \space CABLE!}$$**
6) 3x LEDs of different colors, plus 3x 220Ω resistors → **$${\color{blue}LEDs\space optional}$$**
7) 1x extra-bright LED for camera flash, plus 1x 220Ω resistors → **$${\color{blue}LED\space optional}$$**
8) Powerbank (to make it mobile) -- I have plans to add instructions for a battery build.

**Wiring Diagram**  
• This image shows how to wire up the camera buttons if you are not using the ePaper Hat.  
• It also shows the wiring of optional LEDs.  
<br>
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/wiring_diagram.png' width='650'>

**Setup Waveshare ePaper Display**  
• If you are using the Waveshare 2.7-inch GPIO hat, all you need to do is seat the hat on your Pi.  
• If you're using a different/wired Waveshare display, refer to the GPIO diagram and table below or the image above.
<br>

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/waveshare_Pi02W_setup.jpg' align='left' width='550'>  
  
<br>  

| ePaper Pin | Pi GPIO Pin | 
|------------|------------|  
| VCC | 3.3V |  
| GND | GND |
| DIN | 10 (MOSI) |
| CLK | 11 (SCLK) |
| CS | 8 (CE0) |
| DC | 25 |
| RST | 17 |
| BUSY | 24 |  

 <br><br>

**Connect Camera Buttons**  
• If you are using the Waveshare 2.7-inch GPIO hat, all you need to do is seat the hat on your Pi.  
• If you're using a different Waveshare display, refer to the GPIO diagram and table below.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/Waveshare_2in7_GPIOhat_pins.jpg' align='left' width='400'>  
<br>  

| Button Function | Pi GPIO Pin |
|------------|------------|  
| Take Photo/Select | 5 |  
| Up Selection | 13 |
| Down Selection | 6 |
| Open Menu/Cancel | 19 |  

<br><br>

**Optional Camera LEDs**  
• The addition of LEDs to the camera is optional but adds a little bit of flare to the camera's functionality.  
• If you are using the Waveshare 2.7-inch GPIO hat, you'll need to use a breakout board or some kind of prototype board to connect the LEDs.  
[Example of Breakout Board](https://www.amazon.com/dp/B0DMNJ17PD?ref=ppx_yo2ov_dt_b_fed_asin_title)  
[Example of Prototype Board](https://www.amazon.com/dp/B08C2XSTK2?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1)  
• Refer to the GPIO table below if you are adding LEDs to your camera.
| LED | Pi GPIO Pin |
|------------|------------|  
| Green | 16 |  
| Yellow | 12 |
| Red | 20 |
| Flash | 23 |

**Connect the Camera**  
• For this project, I used the official Raspberry Pi Camera module.  
• Others may work, but you may need to install specific device drivers.  
• Before connecting the camera (or anything for that matter) power off your Pi.  
• Be careful with the connector clips on the Pi and camera, as they are delicate and can break!  
• Pay close attention to how you connect the ribbon cable to both your Pi and your camera.  
• The copper for both ends of the ribbon cable should face as shown below.  

<img src='' align='left' width='400' alt='connect camera'>  
<br>  

# Install the Raspberry Pi Operating System #
**Flash the OS with Raspberry Pi Imager**  
[Download Raspberry Pi Imager here](https://www.raspberrypi.com/software/)  
<br>
• To start, select Raspberry Pi Zero 2W from the device selection list.  
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/select_board.jpg' align='left' width='400'>  
<br><br><br><br>
• For the operating system, select "Raspberry Pi OS (other)".  
<br>
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/os_other.jpg' align='left' width='300'>  
<br><br><br><br>
• Then select "Raspberry Pi OS Lite (64 bit)".  
<br>
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/OS_lite64.png' align='left' width='300'>  
<br><br><br><br>
• Now select the drive where your SD card is stored.  
<br>
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/storage.jpg' align='left' width='400'>  
<br>  
• Click "NEXT".  

**Use OS Customization?**  
*→ You need to configure a few custom settings so you can access WiFi and SSH into your Pi.*  
• Click on the "EDIT SETTINGS" button.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/edit_custom_settings.png' width='500'>  

• Keep the username as "pi" and keep the default password as "raspberry" for now.  
• You can change the password later, but the username **MUST** stay as "pi".  
• Under "Configure Wireless LAN", enter your WiFi SSID, WiFi password and select your country.  
<br>
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/general_settings.png' width='400'>
<br>  
• Keep the SERVICES settings to enable SSH as they are and click "SAVE" to continue.  
<br>
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/setup_ssh.jpg' width='500'>  
<br>
• Click "YES", and then double check the disc you'll be writing to. All data will be erased.  
• Click "CONTINUE" to begin writing the OS.  
• Once Imager has finished, you can eject the card and insert it into your Pi.  
<br>
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/OS_write_complete.png' width='500'>  
  
### Get Pi's IP address  
• To create an SSH session, you need to determine your Pi's IP address.  
• Connect your Pi to your computer via a USB cable.
> [!IMPORTANT]
> * It is essential that USB cable you connect to your Pi is a **DATA** cable.  
> * Some cables are strictly for charging and will not transfer data.  

• Open the terminal from your computer and enter:  
```
ping pi -n 1
```
• The terminal will attempt to verify the status of your Pi and return its IP address.  
• Write down the IP address, you will use this to SSH into your Pi.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/ping_pi.png' width='500' align='left'>
<br><br><br><br><br><br><br>

### SSH into Pi  
• Once you have the IP, you can SSH into your pi to complete the installation.  
• Replace the IP below with your IP.  
• Enter your password and press Enter.  
<br>
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/ssh_IP_pw.png' width='500' align='left'>  
<br><br>
If you get a warning like the one below, approve it by typing "yes".
<br><br>
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/ssh_warning.jpg' width='700' align='left'>  
<br><br><br><br><br>
  
### Update Pi
• After flashing, it is always recommended to update and upgrade  the OS.  
(This process will likely take a couple minutes time to complete.)  
```
sudo apt update && sudo apt -y full-upgrade
```

# Install Modules #  
(Installing each module will likely take a couple minutes to complete.)  

### Install picamzero
• This project makes use of the picamzero module to take photos.  
```
sudo apt install python3-picamzero -y
```
<!--
• Use the terminal to take a test photo after picamzero has been installed.  
```
rpicam-still -o image.jpg
```
• The terminal will create an image. After it's done, use the "ls" command to verify that a file was created.
-->

### Install Git  
• OS Lite does not include Git, so you will need to install it for this project.
```
sudo apt install git -y
```

### Install gpiozero  
• This project uses the gpiozero module to interface with buttons and LEDs.  
• gpiozero is a library that simplifies interacting with GPIO (General Purpose Input/Output) pins the  Pi.  
• OS Lite does not include gpiozero, so you will need to install it for this project.  
[gpiozero info, docs and recipies](https://gpiozero.readthedocs.io/en/latest/)
```
sudo apt install python3-gpiozero -y
```

## Enable SPI ##
• SPI (Serial Peripheral Interface) must be enabled to use the ePaper display.  
• To asccess the Pi config menu:
```
sudo raspi-config
```
• Use the arrow keys to select option 5 "Interfacing Options".  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/SPI_1.jpg' width='400' align='left'>  
<br><br><br><br><br><br><br><br>  

• Then select P4 "SPI".  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/SPI_2.jpg' width='400' align='left'>  
<br><br><br><br><br><br><br><br>  

• Select "Yes" to enable SPI.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/SPI_3.jpg' width='400' align='left'>  
<br><br><br><br><br><br><br><br><br><br><br>  

• Select "Yes" to reboot your Pi and apply config changes.  
• NOTE: If not prompted to reboot, select Finish from the config menu and manually reboot in the terminal - sudo reboot  
<br>
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/SPI_4.jpg' width='400' align='left'>  
<br><br><br><br><br><br><br><br><br><br><br>  


> [!IMPORTANT]
> * This project makes use of ePaper displays manufactured by WaveShare.  
> * Installing this project will install drivers for ALL WaveShare displays and save them into the directory "waveshare_epd".  
> * To use a particular display, you will need to edit the line near the top of "main.py" that looks like this:  
> ``` from waveshare_epd import epd2in7_V2 ```  
edit the part "epd2in7_V2" to match the name of your display.


## When Pi Starts Up, Start Camera ##  
• To make the camera start when the Pi boots up, you'll need to do a couple things.  
• Open the crontab...  
```
sudo crontab -e
```
• Select the first option for the editor.  
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/crontab_notice.jpg' width='500' align='left'>  
<br><br><br><br><br><br>  

• Add the folowwing to the bottom of the file.  
```
@reboot python3 /home/pi/ePaper-Pi-Cam/main.py &
```
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/crontab_setting.jpg' width='600' align='left'>  
<br><br><br><br><br><br>  

• Ctrl-X to exit, then Y to save, and Enter to confirm.  
• Then reboot the Pi
```
sudo reboot
```



### Project Resources & Notes for Future Updates/To-Do 
**Picamzero Documents**  
[Docs Recipes](https://picamera.readthedocs.io/en/release-1.13/)
[Getting Started](https://raspberrypifoundation.github.io/picamera-zero/)
[Picamera Project Docs](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/0)  
[Using Picamera2 Functions with Picamzero](https://raspberrypifoundation.github.io/picamera-zero/picamera2/)    
[Picamzero API Documentation](https://raspberrypifoundation.github.io/picamera-zero/api_docs/)  
[PiCamzero Timelapse option](https://raspberrypifoundation.github.io/picamera-zero/camera/)

**GPIO Zero Install & Recipies**  
[Install gpiozero](https://gpiozero.readthedocs.io/en/stable/installing.html)  
[Recipies → light sensor - for auto flash](https://gpiozero.readthedocs.io/en/stable/recipes.html#light-sensor)  

**Waveshare ePaper Info**  
[ePaper Tutorials](https://dev.to/ranewallin/getting-started-with-the-waveshare-2-7-epaper-hat-on-raspberry-pi-41m8)  
[Waveshare screen rotation -- MAYBE](https://www.waveshare.com/wiki/4.3inch_DSI_LCD)  
[More Waveshare info - Python Screen rotation / partial refresh options](https://www.waveshare.com/wiki/E-Paper_API_Analysis#Python)  
[Waveshare ePaper setup -- complete massive walk-through](https://peppe8o.com/epaper-eink-raspberry-pi/)  
[Waveshare 2.7" with buttons -- Walkthrough with Drawing examples](https://dev.to/ranewallin/getting-started-with-the-waveshare-2-7-epaper-hat-on-raspberry-pi-41m8)  

### Other Resources ###
[How to Run a Script on Startup for Raspberry Pi - by Sam Westby Tech](https://www.youtube.com/watch?v=Gl9HS7-H0mI)  
[Raspberry Pi Headless Setup for ssh - by Sam Westby Tech](https://www.youtube.com/watch?v=9fEnvDgxwbI)  
[Headless Pi Setup Documentation](https://www.raspberrypi.com/documentation/computers/configuration.html#setting-up-a-headless-raspberry-pi)  
[How to Install Git](https://github.com/git-guides/install-git)  
[Raspberry Pi Official Camera Module Documentation](https://www.raspberrypi.com/documentation/accessories/camera.html)  


### To-Do
- [ ] Increase flash duration for better exposure. ! Priority ! 
- [ ] Audit code for efficiencey - remove/refine classes / modules -- logging
- [ ] Partial refresh of display
- [ ] Menu Config Options for: Screen Rotation, Camera Eposure, Screen & Photo Resolution
- [ ] Select a photo for splashscreen from manual scroll
- [ ] Long Term: Wifi connect to download photos?
- [ ] Long Term: Web UI?
- [ ] Long Term: Light sensor for auto-flash?
- [x] Buttons to navigate through past photos.
- [x] Delete single images
- [x] Delete ALL images
- [x] Settings window to change indoor/outdoor brightness, whitebalance, etc.
- [x] Possibly add a bright LED for flash?
