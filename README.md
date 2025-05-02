<!--

https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax

> [!NOTE]
> Useful information that users should know, even when skimming content.

> [!TIP]
> Helpful advice for doing things better or more easily.

> [!IMPORTANT]
> Key information users need to know to achieve their goal.

> [!WARNING]
> Urgent info that needs immediate user attention to avoid problems.

> [!CAUTION]
> Advises about risks or negative outcomes of certain actions.

-->

# ePaper-Pi-Cam
Take photos with Raspberry Pi and show them on a WaveShare ePaper display.
Buttons to loop through past photos.

# Wire up hardware
**ePaper Display** 
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

**Camera Buttons** 
| Button Function | Pi GPIO Pin |
|------------|------------|  
| Take Photo/Select | 5 |  
| Open Menu/Cancel | 14 |
| Up Selection | 6 |
| Down Selection | 13 | 

**Camera LEDs** 
| LED | Pi GPIO Pin |
|------------|------------|  
| Green | 20 |  
| Yellow | 16 |
| Red | 12 |


[Circut Designer diagram](https://app.cirkitdesigner.com/project/d28ef6a1-0fe4-4ffe-82af-59cbab05e6b5)

## Install the Raspberry Pi Operating System
**Flash the OS with Raspberry Pi Imager**  
[Download it here](https://www.raspberrypi.com/software/)
1) Select Raspberry Pi Zero 2W from boards selection list.  
2) Select PiOS64bit lite  
3) Select the drive where your SD card is stored
4) Select "Next"  

**Apply Custom Settings**  
Configure some custom settings so you can ssh into your Pi headless, ect.  
![Image](https://github.com/user-attachments/assets/4973a321-0e3e-4c67-99c8-3fd343964e59)  

5) Go to Advnced settings, add your wifi info  
6) Suggest keeping login info default for now
7) 

### Update Pi
```
sudo apt update && sudo apt -y full-upgrade
```

### Install Git  
OS Lite does not include Git, so you will need to install it for this project.
```
sudo apt install git
```

### Install picamzero
This project makes use of the picamzero module to take photos.
```
sudo apt install python3-picamzero
```

> [!IMPORTANT]
> * This project makes use of ePaper displays manufactured by WaveShare.  
> * Installing this project will install drivers for ALL WaveShare displays and save them into the directory "waveshare_epd".  
> * To use a particular display, you will need to edit the line near the top of "mainprog.py" that looks like this:  
> ``` from waveshare_epd import epd2in7_V2 ```  
edit the part "epd2in7_V2" to match the name of your display.

### Project Resources
**Picamzero Documents**  
[Getting Started](https://raspberrypifoundation.github.io/picamera-zero/)
[Picamera Project Docs](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/0)  
[Using Picamera2 Functions with Picamzero](https://raspberrypifoundation.github.io/picamera-zero/picamera2/)    
[Picamzero API Documentation](https://raspberrypifoundation.github.io/picamera-zero/api_docs/)  
[ePaper Tutorials](https://dev.to/ranewallin/getting-started-with-the-waveshare-2-7-epaper-hat-on-raspberry-pi-41m8)  

**Waveshare ePaper Info**  
[Waveshare screen rotation -- MAYBE](https://www.waveshare.com/wiki/4.3inch_DSI_LCD)  
[More Waveshare info - Python Screen rotation / partial refresh options](https://www.waveshare.com/wiki/E-Paper_API_Analysis#Python)  
[Waveshare ePaper setup -- complete massive walk-through](https://peppe8o.com/epaper-eink-raspberry-pi/)  
[Waveshare 2.7" with buttons -- Walkthrough with Drawing examples](https://dev.to/ranewallin/getting-started-with-the-waveshare-2-7-epaper-hat-on-raspberry-pi-41m8)  

### Other Resources ###
[How to Run a Script on Startup for Raspberry Pi - by Sam Westby Tech](https://www.youtube.com/watch?v=Gl9HS7-H0mI)

[Raspberry Pi Headless Setup for ssh - by Sam Westby Tech](https://www.youtube.com/watch?v=9fEnvDgxwbI)

[Headless Pi Setup Documentation](https://www.raspberrypi.com/documentation/computers/configuration.html#setting-up-a-headless-raspberry-pi)  

[How to Install Git](https://github.com/git-guides/install-git)

### To-Do
- [x] Buttons to navigate through past photos.
- [ ] Button to delete single images
- [ ] Button to delete ALL images
- [ ] Settings window to change indoor/outdoor brightness, whitebalance, etc.
- [ ] Possibly add a bright LED for flash?
