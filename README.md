# cygun
Lightgun for Windows with Python and an USB webcam

> [!IMPORTANT]
> The project is an early alpha and still needs a lot of maintenance.




## Setup
If you don't have Python on your PC or don't want to install it, you can use the WinPyython project.
This also has the advantage that you do not necessarily have to update the libraries in it to avoid later API changes.
And its portable.

you can download it from there if you like:

[https://sourceforge.net/projects/winpython/files/WinPython_3.12/3.12.4.1/Winpython64-3.12.4.1dot.exe/download] 

<br><br>
After unpacking, we have a folder with the name WPy64-31241, which we open. 
There we start “WinPython Command Prompt.exe” and first install all the required libraries.
```
python.bat -m pip install configparser numpy opencv-contrib-python pygame pygrabber pynput pywin32 pyserial
```
