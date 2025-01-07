import configparser
import os
import sys
import subprocess
import time
import configparser

def clear_gui():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_config():
    if not os.path.exists('CyGunConf.ini'):
        config = configparser.ConfigParser()
        config['player1'] = {
            'camera_name': 'None',
            'recorded_video_frame_width': '1280',
            'recorded_video_frame_height': '720',
            'recognized_contour_area_len': '0',
            'mouse_output_style': 'ctype_abs',
            'arduino_pid': '0',
            'arduino_vid': '0',
            'arduino_hw_name': 'None',
            'calibdata_oben_links_x': '0',
            'calibdata_oben_rechts_x': '1280',
            'calibdata_unten_links_x': '0',
            'calibdata_unten_rechts_x': '1280',
            'calibdata_oben_links_y': '0',
            'calibdata_oben_rechts_y': '0',
            'calibdata_unten_links_y': '720',
            'calibdata_unten_rechts_y': '720',
            'keymapping_button_fire': '0x00',
            'keymapping_button_reload': '0x00',
            'keymapping_button_opt1': '0x00',
            'keymapping_button_opt2': '0x00',
            'keymapping_button_opt3': '0x00',
            'keymapping_button_opt4': '0x00',
            'keymapping_button_startsync': '0x00',
            'ctypes_incremental_reset_pos': 'desktop',
            'ctype_mouse_inc_reset_every_n_missed_frames': '10',
            'ctypes_mouseclick_sleep_duration': '0.1',
            'ctypes_keyboard_sleep_duration': '0.1',
            'firebutton_working_style': 'direct',
            'shoot_offscreen4reload': 'offscreen'
        }
        config['player2'] = {
            'camera_name': 'None',
            'recorded_video_frame_width': '1280',
            'recorded_video_frame_height': '720',
            'recognized_contour_area_len': '0',
            'mouse_output_style': 'ctype_abs',
            'arduino_pid': '0',
            'arduino_vid': '0',
            'arduino_hw_name': 'None',
            'calibdata_oben_links_x': '0',
            'calibdata_oben_rechts_x': '1280',
            'calibdata_unten_links_x': '0',
            'calibdata_unten_rechts_x': '1280',
            'calibdata_oben_links_y': '0',
            'calibdata_oben_rechts_y': '0',
            'calibdata_unten_links_y': '720',
            'calibdata_unten_rechts_y': '720',
            'keymapping_button_fire': '0x00',
            'keymapping_button_reload': '0x00',
            'keymapping_button_opt1': '0x00',
            'keymapping_button_opt2': '0x00',
            'keymapping_button_opt3': '0x00',
            'keymapping_button_opt4': '0x00',
            'keymapping_button_startsync': '0x00',
            'ctypes_incremental_reset_pos': 'desktop',
            'ctype_mouse_inc_reset_every_n_missed_frames': '10',
            'ctypes_mouseclick_sleep_duration': '0.1',
            'ctypes_keyboard_sleep_duration': '0.1',
            'firebutton_working_style': 'direct',
            'shoot_offscreen4reload': 'offscreen'
        }
        config['debug'] = {
            'show_recorded_video': 'False',
        }
        config['whiteframe'] = {
            'frame_boarder_size': '30',
        }

        with open('CyGunConf.ini', 'w') as configfile:
            config.write(configfile)

def askforplayer():
    clear_gui()
    print(" ----- Setup -----")
    print()
    print(" -- select player to edit")
    print(" 1 :  Player 1")
    print(" 2 :  Player 2")
    print()
    sel = input("Select:")
    if sel.isnumeric() == False:
        sel = 99
    if sel == '2':
        clear_gui()
        print("Player two is still under development and is not yet working.")
        print()
        print(" >>>>  Player 1 was automatically selected.")
        time.sleep(2)
        return "player1"
    else:
        return "player1"

def startview():
    clear_gui()
    print(" ----- Setup -----")
    print()
    print(" -- webcam")
    print(" 1 :  init new webcam")
    print(" 2 :  sync rectangle frame")
    print()
    print(" -- arduino")
    print(" 3 :  setup serial connection")
    print()
    print(" -- system")
    print(" 4 :  HID injection type")
    print(" 5 :  keymapping")
    print()
    print(" 0 :  exit")
    print()
    sel = input("Select:")
    if sel.isnumeric() == False:
        sel = 99
    return sel

def askinjection():
    clear_gui()
    print(" ----- Setup -----")
    print()
    print(" -- use SendInput ")
    print(" 1 :  keyboard/mouse absolute")
    print(" 2 :  keyboard/mouse incremental")
    print()
    sel = input("Select:")
    if sel.isnumeric() == False:
        sel = 99
    return sel

def runscript(new_script_name):
    current_script_path = os.path.abspath(__file__)
    python_interpreter_path = sys.executable
    new_script_path = os.path.join(os.path.dirname(current_script_path), new_script_name)
    subprocess.run([python_interpreter_path, new_script_path])

def testmainselection():
    usrsel = startview()
    if usrsel == '1':
        runscript("setup_usb_webcam.py")
        time.sleep(4)
    elif usrsel == '2':
        runscript("setup_framedetection.py")
    elif usrsel == '3':
        runscript("setup_serial_con.py")
    elif usrsel == '4':
        setinject = askinjection()
        if int(setinject) <= 2:
            return setinject
    elif usrsel == '5':
        runscript("setup_keymapping.py")
    elif usrsel == '0':
        return '100'
    else:
        clear_gui()
        print()
        print(" Wrong input! Try harder next time.")
        time.sleep(2)
    return '99'

def write_config_to_file(confsection, confname, confvalue):
    out = True
    try:
        myconfigparser = configparser.ConfigParser()
        myconfigparser.read('CyGunConf.ini')
        myconfigparser.set(confsection,confname, confvalue)
        with open('CyGunConf.ini', 'w') as updtini:
            myconfigparser.write(updtini)
    except Exception as e:
        print(e)
        time.sleep(2)
        out = False
    return out

if __name__ == "__main__":
    generate_config()
    editplayername = askforplayer()
    while True:
        getval = testmainselection()
        if getval == '100':
            exit()
        if getval == '1':
            #save mouse abs for playerx
            isit = write_config_to_file(editplayername, 'mouse_output_style', "ctype_abs")
            if isit == True:
                print("Settings saved!")
                time.sleep(1)
            else:
                print("something went wrong!")
                time.sleep(1)
        if getval == '2':
            #save mouse inc for playerx
            isit = write_config_to_file(editplayername, 'mouse_output_style', "ctype_inc")
            if isit == True:
                print("Settings saved!")
                time.sleep(1)
            else:
                print("something went wrong!")
                time.sleep(1)

