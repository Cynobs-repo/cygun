# cygun
Lightgun for Windows written in Python with use of a USB webcam

> [!IMPORTANT]
> The project is an early alpha and still needs a lot of maintenance.



## What you need:
+  a USB webcam that delivers at least 60 FPS at 1280x720. (The more the better)
+  Arduino with 328P chip or similar
+  5 Pushbuttons with some wire
+  a decent computer
+  maybe a 3d printer to build your own Lightgun

How it works:<br>
► record frame from camera 

► search for the rectangle and do a bit math 

► uses the calculated Point and send it as mouse position to your windows environement

## Setup
If you don't have Python on your PC or don't want to install it, you can use the WinPyython project.
This also has the advantage that you do not necessarily have to update the libraries in it to avoid later API changes.
And its portable.

you can download it from there if you like:<br>
[https://sourceforge.net/projects/winpython/files/WinPython_3.12/3.12.4.1/Winpython64-3.12.4.1dot.exe/download] 
<br>
After unpacking, we have a folder with the name WPy64-31241, which we open. 
There we start “WinPython Command Prompt.exe” and first install all the required libraries.
```
python.bat -m pip install configparser numpy opencv-contrib-python pygame pygrabber pywin32 pyserial
```
Once this is done, we copy the Windows batch scripts “run_cygun.bat”, “run_setup.bat” and “run_frame.bat” into the “scripts” folder.
These are used to start Cygun in the WinPython environment. If you have installed Python directly, you can also start the corresponding scripts directly. The batch scripts are only used to activate the “virtual” Python environment.
<br>
Then copy the cygun folder and its contents to “..\WPy64-31241\python-3.12.4.amd64\”
<br>
That's it with the copying back and forth.
<br><br>
## Arduino Setup

We use an Arduino to transmit the keystrokes for the fire button and four option buttons to the PC. I used a cheap one with a 328P chip. 
Since there is no second player yet, it is sufficient to flash the Arduino with the enclosed software from the “Arduino” folder and solder the buttons as shown in the following circuit diagram.

<img src="https://github.com/Cynobs-repo/cygun/blob/main/Arduino.png" width="300" />

<br>

+  Arduino Pin 2 -- Fire button ------ GND
+  Arduino pin 3 -- Option button 1 -- GND
+  Arduino pin 4 -- Option button 2 -- GND
+  Arduino pin 5 -- Option button 3 -- GND
+  Arduino Pin 6 -- Option button 4 -- GND
  
<br>
If you open the serial monitor in the Arduino IDE after flashing, you should receive the text “RRRRRR” from the Arduino if everything went well.

## Setup your PC:
First we start the “run_setup.bat” script. This starts the Python script “start_setup.py” in the cygun folder.
This is a simple tool to start the individual setup steps.

When the script is started for the first time, a Config.ini file is created which is later filled by the other scripts.
When we start the setup tool we are asked whether we want to set the settings for player one or player two. (Note: Player two does not yet work and is not yet activated)
```
 ----- Setup -----

 -- select player to edit
 1 :  Player 1
 2 :  Player 2

Select:
```

You will then be taken to the main view:
````
 ----- Setup -----

 -- webcam
 1 :  init new webcam
 2 :  sync rectangle frame

 -- arduino
 3 :  setup serial connection

 -- system
 4 :  HID injection type
 5 :  keymapping

 0 :  exit

Select:
````
The points should be worked through from top to bottom before the light gun is put into operation.

<br><br>

### Selection 1 : init new webcam
Starts the script: setup_usb_webcam.py

Searches the PC for connected image recording devices and lists all those it could find.
Here you select the webcam to be used for the lightgun.

````

Please select the camera which will be used for the lightgun:

ID: 0  name: HD USB Camera
ID: 1  name: StreamAnimations cam
ID: 2  name: Twitch Virtual Cam
ID: 3  name: OBS Virtual Camera

Enter ID:0
````
The selected webcam is then tested at which resolution and how many FPS can be expected.
````

checking camera capabilities...

warm up at 640x360
testing 640x360...
warm up at 1280x720
testing 1280x720...
warm up at 1920x1080
testing 1920x1080...
````
Once this has been completed, the results are listed.
````

Your camera model name: HD USB Camera

select the resolution to work with:

Select: 0  resolution: 640x360  at max. 187.47 fps
Select: 1  resolution: 1280x720  at max. 121.94 fps
Select: 2  resolution: 1920x1080  at max. 59.06 fps

Enter Number:1

````

Here you should preferably choose a resolution that has a high FPS value. I would preferably select 1280x720 or lower.

After the selection, the values are saved and you return to the main setup screen.
<br><br><br>
### Selection 2 : sync rectangle frame
Starts the script: setup_framedetection.py


Since we want to determine our mouse interpolation with the help of the frame on the monitor, we need to find out how large the rectangle to be detected must be.
To do this, we position the lightgun in the position from which we want to play later and point it towards the TV.

The script also tells you to do this at the start.

````
    Please set up the lightgun now so that it is in the same position
    as if you wanted to shoot at the center of the screen later.
    The camera must capture the entire screen.
    When you press any key, a full screen animation starts and the synchronization begins.

    Please do not move the camera during the process.

Press any key to continue...
````


An animation then runs which displays a white rectangle that gets larger on a black background.
When the white rectangle has reached the edge of the monitor, the script ends and saves the determined length.



<br><br><br>
### Selection 3 : setup serial connection
Starts the script: setup_serial_con.py

Before starting this script, the Arduino must be flashed with the supplied firmware. 
After starting, the COM ports are searched and all devices found are listed.

````

searching COM ports...
 0  = COM4  #  USB-SERIAL CH340 (COM4)
 1  = COM1  #  Kommunikationsanschluss (COM1)

Enter select number for Arduino COM Port:
````

After selection, the device properties are displayed

````

You selected: Kommunikationsanschluss (COM1)

--- Hardware details:
Name (COM-port): COM1
Description: Kommunikationsanschluss (COM1)
HWID: ACPI\PNP0501\0
Manufacturer: (Standardanschlusstypen)
----------------------------------------

Press any key to continue...

````

The connection is tested by pressing any button.
If this is successful, a short message appears to indicate that the values have been saved.
You then return to the main menu


<br><br><br>
### Selection 4 : HID injection type
Does not start a script but changes the CyGunConf.ini directly

There are currently two input methods which both transmit the movements and keystrokes to Windows via SendInput.
One is absolute mouse positioning and the other is incremental.

The absolute one is quite robust.

The incremental one is still under development.
When this is started, the mouse position is still read in via the Windows system. Then the mouse pointer is moved to the top left corner when it leaves the monitor's detection area. As soon as contact is re-established, the system corrects itself and moves the mouse pointer to the newly detected position.

````

 ----- Setup -----

 -- use SendInput
 1 :  keyboard/mouse absolute
 2 :  keyboard/mouse incremental

Select:

````
The value “mouse_output_style” in the CyGunConf.ini is changed.
If you want to change it manually, you can choose between the two input values “ctype_inc” and “ctype_abs”.

<br><br><br>
### Selection 5 : keymapping
Starts the script: setup_keymapping.py

Here you can map the keys of the lightgun to keyboard and mouse keys.

````
Keymapping for CyGun:

fire:   0x1
reload:   0x2
startsync:   0x00
opt1:   0x00
opt2:   0x00
opt3:   0x00
opt4:   0x00


Options:
1: change mapping
2: save and exit
3: exit
please choose:
````


Selecting 1 takes you directly to the next menu in which you can select the button to be changed.

````
Which button do you like to change?

1: fire
2: reload
3: startsync
4: opt1
5: opt2
6: opt3
7: opt4

select:
````
Now select the key that is to be changed/assigned and you will immediately be prompted to press the desired key on the keyboard or mouse.
There is a small bug: If a mouse click is to be recognized, please do not click in the shell input window but anywhere on the desktop. 
If you click in the window, the mouse click is not recognized and the script hangs.

The recognized characters are displayed in hexadecimal values.
When you are finished, you can save the keystrokes by clicking on “save and exit”.

Key properties:

+ 1: fire = fire button of the light gun. This is the button that is connected to pin 2 on the Arduino. 

+ 2: reload = virtual button. If you want to set the lightgun to reload as soon as you shoot outside the screen, the corresponding reload button must be defined here.

+ 3: startsync = virtual key To set up the lightgun to the player and his position and to calculate out distortions we need the four corner points of the monitor. If this button is pressed later when the CyGun script is running, a black screen appears on which targets are displayed. You have to aim at these one after the other and shoot at them. The software determines the boundary coordinates of the light gun to the mouse. Once all four corner points have been recognized, the new parameters are applied immediately and the setup tool is closed again.

+ 4: opt1 ╗
+ 5: opt2 ╣
+ 6: opt3 ╣
+ 7: opt4 = The four option buttons are connected to the Arduino on pins 3 to 6 and can be freely assigned. You can also enter the same buttons here as for the virtual buttons to call up their function. As an example, you can assign the “reload” button as well as any option button with “r” for reloading. The number of bullets is then replenished when the key is pressed, just like when shooting off-screen. If you place the same key as defined in “startsync” on an option button, you can call up the synchronization tool by pressing it.

Options in the CyGunConf.ini which have not yet made it into the settings menu:

+ 'ctypes_incremental_reset_pos':<br>
  When the Lightgun is started with the incremental SendInput mouse control, the software either adopts the mouse position from Windows or snaps to it by moving the pointer to the top left corner. The following    options are available:
  + 'desktop' - Lightgun takes over Windows position
  + 'leftup' - The mouse pointer is moved to the top left corner at startup
<br>

+ 'ctype_mouse_inc_reset_every_n_missed_frames':<br>
  If the Lightgun is running with the incremental SendInput mouse control, the pointer is reset after the unsuccessful detection of the position after n frames. Default value 10
<br>

+ 'firebutton_working_style':<br>
  Setting whether either a short pulse is emitted when the fire button is pressed or the pressed button is transmitted as pressed until it is released again. Possible settings:
  + 'direct' - send button input until the button is released again
  + 'single' - button is pressed and released again after a short period of time.
<br>

+ 'ctypes_mouseclick_sleep_duration':<br>
  Time in seconds how long to wait between pressing and releasing the mouse buttons. Too small values are no longer recognized by games.
<br>

+ 'ctypes_keyboard_sleep_duration':<br>
  Time in seconds how long to wait between pressing and releasing the keyboard keys. Too small values are no longer recognized by games.
<br>

+ 'shoot_offscreen4reload':<br>
  Set whether or not to reload when shooting offscreen.
  Possible settings:
  + 'offscreen' - Enable reload when aiming and shooting offscreen
  + 'none' - Deactivates the function
<br>
 
+ In the “debug” section:<br>
  + 'show_recorded_video': 'False' If you set the value to “True”, the recorded video image and the recognized frame are displayed in a window
<br>

+ In the “whiteframe” section:
  + 'frame_boarder_size': Width of the white rectangular frame on the screen in pixels

<br>

### After you have worked through all the setup steps, you should next run the batch script “run_frame.bat”.
This starts the Python script “white_frame.py”
Use the script to draw the white frame over everything on the monitor. If you are on the Windows desktop, the taskbar is respected and not painted over. If you want to play on the desktop, it is recommended to set the taskbar to “hide automatically” to avoid misinterpretation of the position detection. If you start any program in full screen, this is detected and the frame is adjusted. So far it has been tested with “House of the Dead Remake” and on the Windows desktop.

<br>

### Now you can start the batch script “run_cygun.bat” which executes the Python script “cygun_run.py”.
The script now reads the created config, connects to the Arduino and the webcam and takes over the mouse control.
Now the CyGun should work :)


