import cv2
import time
import win32com.client
import os, sys
from pygrabber.dshow_graph import FilterGraph
import configparser

def write_to_ini(camname, resx, resy, pnum):
    try:
        path2configstr = 'CyGunConf.ini'
        myconfigparser = configparser.ConfigParser()
        myconfigparser.read(path2configstr)
        if pnum == 1:
            myconfigparser.set('player1', 'camera_name', str(camname))
            myconfigparser.set('player1', 'recorded_video_frame_width', str(resx))
            myconfigparser.set('player1', 'recorded_video_frame_height', str(resy))
        elif pnum == 2:
            myconfigparser.set('player2', 'camera_name', str(camname))
            myconfigparser.set('player2', 'recorded_video_frame_width', str(resx))
            myconfigparser.set('player2', 'recorded_video_frame_height', str(resy))
        with open(path2configstr, 'w') as updtini:
            myconfigparser.write(updtini)
    except Exception as e:
        print(f"Error occured while writing ini file. Error: {e}")
        return False

    return True

def clear_gui():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_user_input_int(usrin):
    try:
        val = int(usrin)
        return True
    except ValueError:
        return False

def test_user_input(idu):
    clear_gui()
    if check_user_input_int(idu) == False:
        print()
        print("Wrong input! Should be a number. please restart the script.")
        print("exiting...")
        time.sleep(1)
        exit()

def list_camera_properties(camera_id):
    out = []
    cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print()
        print(f"camera with ID {camera_id} could not get opened.")
        return None

    test_resolutions = [(640, 360), (640, 480), (1280, 720), (1920, 1080), (3840, 2160)]
    for width, height in test_resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if actual_width == width and actual_height == height:
            print(f"warm up at {width}x{height} ")
            warmup_duration = 2
            warmup_start = time.time()
            while time.time() - warmup_start < warmup_duration:
                ret, _ = cap.read()
                if not ret:
                    print()
                    print(f"error while warming up {width}x{height}")
                    break

            print(f"testing {width}x{height}...")
            frame_count = 0
            start_time = time.time()
            test_duration = 2

            while time.time() - start_time < test_duration:
                ret, frame = cap.read()
                if ret:
                    frame_count += 1
                else:
                    print(f"error reading frames at {width}x{height}")
                    break

            end_time = time.time()
            duration = end_time - start_time
            fps = frame_count / duration if duration > 0 else 0
            new = [width, height, fps]
            out.append(new)

    cap.release()
    return out

if __name__ == "__main__":
    if len(sys.argv) == 2:
        playernumber = sys.argv[1]
    else:
        playernumber = 'p1'


    clear_gui()
    graph = FilterGraph()
    allcameras = graph.get_input_devices()

    print("Please select the camera which will be used for the lightgun:")
    print()
    for single in allcameras:
        print(f"ID: {allcameras.index(single)}  name: {single}")
    print()
    camIDforUse = int(input("Enter ID:"))
    test_user_input(camIDforUse)
    print("checking camera capabilities...")
    print()
    camprop = list_camera_properties(camIDforUse)
    if camprop is not None:
        clear_gui()
        print(f"Your camera model name: {allcameras[camIDforUse]}")
        print()
        print("select the resolution to work with:")
        print()
        for entry in camprop:
            print(f"Select: {camprop.index(entry)}  resolution: {entry[0]}x{entry[1]}  at max. {entry[2]:.2f} fps")
        print()
        restouse = int(input("Enter Number:"))
        test_user_input(restouse)
        clear_gui()
        if playernumber == 'p2':
            playernum = 2
        else:
            playernum = 1
        # print()
        # print("Your selection:")
        # print(f"camera model name: {allcameras[camIDforUse]}")
        # print(f"running at {camprop[restouse][0]}x{camprop[restouse][1]}")
        # print()
        # print("Should the settings be saved for player 1 or player 2?")
        # print("1 : Player 1")
        # print("2 : Player 2")
        # playernum = input("Enter 1 or 2:")
        # test_user_input(playernum)
        clear_gui()
        print()
        if int(playernum) == 1:
            print("saving data for player 1")
        elif int(playernum) == 2:
            print("saving data for player 2")
        # else:
            # print("wrong number! didnt saved anything.")
            # time.sleep(1)
            # exit()

        iswritten = write_to_ini(allcameras[camIDforUse], camprop[restouse][0], camprop[restouse][1], int(playernum))
        if iswritten == True:
            print()
            print("Done! ")
