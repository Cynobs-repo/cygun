# cygun
Lightgun for Windows with Python and an USB webcam

> [!IMPORTANT]
> The project is an early alpha and still needs a lot of maintenance.




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
python.bat -m pip install configparser numpy opencv-contrib-python pygame pygrabber pynput pywin32 pyserial
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


