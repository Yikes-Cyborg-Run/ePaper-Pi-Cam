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
Connect the e-ink display's VCC pin to the 3.3V pin on the Pi.  
Connect the e-ink display's GND pin to the GND pin on the Pi.  
Connect the e-ink display's DIN pin to the Pi's GPIO 19 (MOSI).  
Connect the e-ink display's CLK pin to the Pi's GPIO 23 (SCLK).  
Connect the e-ink display's CS pin to the Pi's GPIO 24 (CE0).  
Connect the e-ink display's DC pin to the Pi's GPIO 25.  
Connect the e-ink display's RST pin to the Pi's GPIO 17.  
Connect the e-ink display's BUSY pin to the Pi's GPIO 18.   

## Install the Raspberry Pi Operating System
**Flash the OS with Raspberry Pi Imager**  
[Download it here](https://www.raspberrypi.com/software/)
1) Select Raspberry Pi Zero 2W from boards selection list.  
2) Select PiOS64bit lite  
3) Select the drive where your SD card is stored

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

### Other Resources ###
[How to Run a Script on Startup for Raspberry Pi - by Sam Westby Tech](https://www.youtube.com/watch?v=Gl9HS7-H0mI)

[Waveshare ePaper setup -- complete massive walk-through](https://peppe8o.com/epaper-eink-raspberry-pi/)

[How to Install Git](https://github.com/git-guides/install-git)

### To-Do
- [x] Buttons to navigate through past photos.
- [ ] Button to delete single images
- [ ] Button to delete ALL images
- [ ] Settings window to change indoor/outdoor brightness, whitebalance, etc.
- [ ] Possibly add a bright LED for Flash?
