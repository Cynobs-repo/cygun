import cv2
import numpy as np
#import pyautogui
from pynput import keyboard, mouse
import ctypes
from win32api import GetSystemMetrics
import win32com.client
from ctypes.wintypes import *
import time
import win32api, win32con
import configparser
import pygame
import sys
import threading
import queue
import serial
import serial.tools.list_ports
from pygrabber.dshow_graph import FilterGraph
import base64
import io
import setupimages

#### PC Maus Input Gedöns

def set_startup_mouse_values():
    # Set DPI awareness  (Windows 10 and 8)
    errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(2)
    # Disable mouse acceleration
    setsetting_raw_arrry = [0, 0, 0]
    setsetting_mouse_acc = (ctypes.c_int * len(setsetting_raw_arrry))(*setsetting_raw_arrry)
    errorCode = ctypes.windll.user32.SystemParametersInfoA(4, 0, setsetting_mouse_acc, 0)
    # set mouse speed- abs = 20 incremental - set var ( in unsrem Fall 12)
    ctypes.windll.user32.SystemParametersInfoA(113, 0, mouse_speed_set, 0)



### ctypes SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long),
                ("y", ctypes.c_long)]

class CtypesMouseKeyboard:
    def __init__(self, raw_inc_reset_pos, raw_mouse_res_n_frames_frames, raw_mouseclick_sleep_dur, raw_kbdclick_sleep_dur):
        self.ctypes_mouseclick_sleep_duration = raw_mouseclick_sleep_dur
        self.ctypes_keyboard_sleep_duration = raw_kbdclick_sleep_dur
        '''
            Startpositions available:
            ### (not working yet) center = center of screen
            leftup = left upper corner
            desktop = use ctype position
        '''
        self.ctypes_incremental_reset_pos = raw_inc_reset_pos
        self.inc_old_position = self.get_inc_start_pos()
        self.inc_reset_counter = 0
        self.ctype_mouse_inc_reset_every_n_missed_frames = raw_mouse_res_n_frames_frames

        # backup mouse speed
        rawspeed = ctypes.c_int()
        ctypes.windll.user32.SystemParametersInfoW(0x0070, 0, ctypes.byref(rawspeed), 0)
        self.backup_mouse_speed = rawspeed.value

        # backup mouse acceleration
        self.backup_mouse_acceleration = self.is_mouse_acceleration_enabled()




    def ctypes_init_incremental_input(self):
        # set mouse speed to 10
        ctypes.windll.user32.SystemParametersInfoA(113, 0, 10, 0)
        # Disable mouse acceleration
        setsetting_raw_arrry = [0, 0, 0]
        setsetting_mouse_acc = (ctypes.c_int * len(setsetting_raw_arrry))(*setsetting_raw_arrry)
        errorCode = ctypes.windll.user32.SystemParametersInfoA(4, 0, setsetting_mouse_acc, 0)

    def ctypes_reset_incremental_input(self):
        # reset mouse speed
        ctypes.windll.user32.SystemParametersInfoA(113, 0, self.backup_mouse_speed, 0)
        # reset mouse acceleration
        setsetting_mouse_acc = (ctypes.c_int * len(self.backup_mouse_acceleration))(*self.backup_mouse_acceleration)
        errorCode = ctypes.windll.user32.SystemParametersInfoA(4, 0, setsetting_mouse_acc, 0)

    def is_mouse_acceleration_enabled(self):
        mouse_params = (ctypes.c_int * 3)()
        success = ctypes.windll.user32.SystemParametersInfoW(0x0003, 0, mouse_params, 0)
        if not success:
            raise ctypes.WinError()
        return mouse_params

    def ctypes_get_display_size(self):
        return (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))

    ### incremental mouse input
    def get_mouse_position(self):
        cursor = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor))
        return cursor.x, cursor.y

    def get_inc_start_pos(self):
        out = [0, 0]
        if self.ctypes_incremental_reset_pos == 'center':
            display_width, display_height = self.ctypes_get_display_size()
            out[0] = display_width // 2
            out[1] = display_height // 2
        elif self.ctypes_incremental_reset_pos == 'desktop':
            fx, fy = self.get_mouse_position()
            out = [fx, fy]
        elif self.ctypes_incremental_reset_pos == 'leftup':
            self.inc_reset_counter = 99
            self.ctype_inc_mouse_position_reset()
        return out

    def ctype_set_mouse_pos_inc(self, x, y):
        # display_width, display_height = self.ctypes_get_display_size()
        #print(f"Mausposition Aktuell: {self.get_mouse_position()}")
        dx = 0
        dy = 0
        if [x, y] != self.inc_old_position:
            dx = x - self.inc_old_position[0]
            dy = y - self.inc_old_position[1]
            self.inc_old_position = [x, y]

            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.mi = MouseInput(dx, dy, 0, 0x0001, 0, ctypes.pointer(extra))
            command = Input(ctypes.c_ulong(0), ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))
            self.inc_reset_counter = 0

    def ctype_inc_mouse_position_reset(self):
        self.inc_reset_counter += 1
        if self.inc_reset_counter >= self.ctype_mouse_inc_reset_every_n_missed_frames:
            display_width, display_height = self.ctypes_get_display_size()
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.mi = MouseInput(-display_width, -display_height, 0, 0x0001, 0, ctypes.pointer(extra))
            command = Input(ctypes.c_ulong(0), ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))
            time.sleep(0.1)
            self.inc_old_position = [0, 0]
            self.inc_reset_counter = 0
            #print(f"RESETPOS: {self.get_mouse_position()}")


    ### abs mouse input
    def ctype_set_mouse_pos_abs(self, x, y):
        display_width, display_height = self.ctypes_get_display_size()
        x = (x * 65535) // display_width + 1
        y = (y * 65535) // display_height + 1
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(x, y, 0, (0x0001 | 0x8000), 0, ctypes.pointer(extra))
        command = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))



    ### ctype mouse click
    def ctypes_mouse_left_click_press(self):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(0, 0, 0, 0x0002, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def ctypes_mouse_left_click_release(self):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(0, 0, 0, 0x0004, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def ctypes_mouse_right_click_press(self):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(0, 0, 0, 0x0008, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def ctypes_mouse_right_click_release(self):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(0, 0, 0, 0x0010, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def ctypes_mouse_left_click_full(self):
        self.ctypes_mouse_left_click_press()
        time.sleep(self.ctypes_mouseclick_sleep_duration)
        self.ctypes_mouse_left_click_release()

    def ctypes_mouse_right_click_full(self):
        self.ctypes_mouse_right_click_press()
        time.sleep(self.ctypes_mouseclick_sleep_duration)
        self.ctypes_mouse_right_click_release()

    ### ctypes keyboardinput

    # Funktion, um eine Taste mit SendInput zu drücken
    def ctypes_pressandrelease_key(self, hex_key):
        vk_code = int(hex_key, 16)  # Hex-Wert in Integer umwandeln
        ki_down = KeyBdInput(wVk=vk_code, wScan=0, dwFlags=0, time=0, dwExtraInfo=None)
        input_down = Input(type=1, ii=Input_I(ki=ki_down))
        ctypes.windll.user32.SendInput(1, ctypes.byref(input_down), ctypes.sizeof(Input))
        time.sleep(self.ctypes_keyboard_sleep_duration)  # Kurz warten
        ki_up = KeyBdInput(wVk=vk_code, wScan=0, dwFlags=0x0002, time=0, dwExtraInfo=None)
        input_up = Input(type=1, ii=Input_I(ki=ki_up))
        ctypes.windll.user32.SendInput(1, ctypes.byref(input_up), ctypes.sizeof(Input))

    def ctypes_input_keyboard_key_press(self, hex_key):
        vk_code = int(hex_key, 16)  # Hex-Wert in Integer umwandeln
        ki_down = KeyBdInput(wVk=vk_code, wScan=0, dwFlags=0, time=0, dwExtraInfo=None)
        input_down = Input(type=1, ii=Input_I(ki=ki_down))
        ctypes.windll.user32.SendInput(1, ctypes.byref(input_down), ctypes.sizeof(Input))

    def ctypes_input_keyboard_key_release(self, hex_key):
        vk_code = int(hex_key, 16)  # Hex-Wert in Integer umwandeln
        ki_up = KeyBdInput(wVk=vk_code, wScan=0, dwFlags=0x0002, time=0, dwExtraInfo=None)
        input_up = Input(type=1, ii=Input_I(ki=ki_up))
        ctypes.windll.user32.SendInput(1, ctypes.byref(input_up), ctypes.sizeof(Input))




class SerialButtonsReading(threading.Thread):
    def __init__(self, port, baudrate, mapping, data_queue):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.mapping = mapping
        self.data_queue = data_queue
        self.running = True

    def run(self):
        """Führt den Thread aus und liest kontinuierlich von der seriellen Schnittstelle."""
        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                while self.running:
                    line = ser.readline().decode('utf-8').strip()
                    if len(line) == 5:  # Nur weiterverarbeiten, wenn der String 5 Zeichen lang ist
                        mapped_data = {key: line[pos] for pos, key in self.mapping.items()}
                        self.data_queue.put(mapped_data)
                    time.sleep(0.01)  # CPU-Entlastung
        except serial.SerialException as e:
            print(f"Serial Error: {e}")

    def stop(self):
        """Stoppt den Thread."""
        self.running = False





class PositionRecorder:
    def __init__(self):
        self.positions = []

    def add_position(self, x, y):
        self.positions.append((x, y))

    def get_eckpunkte(self):
        if not self.positions:
            raise ValueError("Keine Positionen gespeichert.")

        # Minimal- und Maximalwerte für x und y bestimmen
        # min_x = min(pos[0] for pos in self.positions)
        # max_x = max(pos[0] for pos in self.positions)
        # min_y = min(pos[1] for pos in self.positions)
        # max_y = max(pos[1] for pos in self.positions)

        return {
            "oben_links_x": self.positions[0][0],
            "oben_rechts_x": self.positions[1][0],
            "unten_links_x": self.positions[2][0],
            "unten_rechts_x": self.positions[3][0],
            "oben_links_y": self.positions[0][1],
            "oben_rechts_y": self.positions[1][1],
            "unten_links_y": self.positions[2][1],
            "unten_rechts_y": self.positions[3][1]
        }



class GetCornerOverlay(threading.Thread):
    def __init__(self):
        super().__init__()
        # self.image_path = "target.png"
        # self.explosion_images = [
                                # "punch_blast_01.png",
                                # "punch_blast_02.png",
                                # "punch_blast_03.png",
                                # "punch_blast_04.png",
                                # "punch_blast_05.png",
                                # "punch_blast_06.png",
                                # "punch_blast_07.png",
                            # ]
        # self.detection_success_img_path = "con_yes.png"
        # self.detection_fail_img_path = "con_no.png"
        self.running = True
        self.command_queue = queue.Queue()
        self.event_queue = queue.Queue()
        self.detection_status = None


    def load_base64_image(self, base64_data):
        try:
            image_data = base64.b64decode(base64_data)
            image_stream = io.BytesIO(image_data)
            image = pygame.image.load(image_stream, "PNG")
            return image
        except Exception as e:
            print(f"Error loading base64 images: {e}")
            return None

    def run(self):
        pygame.init()
        info = pygame.display.Info()
        screen_width, screen_height = info.current_w, info.current_h
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

        #image = pygame.image.load(self.image_path)
        image = self.load_base64_image(setupimages.target)
        image_rect = image.get_rect()

        #explosion_frames = [pygame.image.load(img) for img in self.explosion_images]
        explosion_frames = [self.load_base64_image(setupimages.strike_01),
                            self.load_base64_image(setupimages.strike_02),
                            self.load_base64_image(setupimages.strike_03),
                            self.load_base64_image(setupimages.strike_04),
                            self.load_base64_image(setupimages.strike_05)]

        #detection_success_img = pygame.image.load(self.detection_success_img_path)
        detection_success_img = self.load_base64_image(setupimages.con_yes)
        #detection_fail_img = pygame.image.load(self.detection_fail_img_path)
        detection_fail_img = self.load_base64_image(setupimages.con_no)
        detection_img = None

        image_rect.center = (screen_width // 2, screen_height // 2)
        positions = [
            (screen_width // 2 - image_rect.width // 2, screen_height // 2 - image_rect.height // 2),  # Mitte
            (20, 20),  # Oben links
            (screen_width - image_rect.width - 20, 20),  # Oben rechts
            (screen_width - image_rect.width - 20, screen_height - image_rect.height - 20),  # Unten rechts
            (20, screen_height - image_rect.height - 20),  # Unten links
        ]

        current_pos = 0

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            try:
                command = self.command_queue.get_nowait()
                if command == "next":
                    self.play_explosion(screen, image, image_rect, explosion_frames)
                    current_pos = (current_pos + 1) % len(positions)
                    image_rect.topleft = positions[current_pos]
                    self.event_queue.put("animation_complete")
                elif command == "success":
                    self.detection_status = "success"
                    detection_img = detection_success_img
                elif command == "fail":
                    self.detection_status = "fail"
                    detection_img = detection_fail_img
                elif command == "clear":
                    self.detection_status = None
                    detection_img = None
            except queue.Empty:
                pass

            screen.fill((0, 0, 0))
            screen.blit(image, image_rect)

            if detection_img:
                detection_rect = detection_img.get_rect()
                detection_rect.bottomright = ((screen_width // 2) + 150, screen_height)
                screen.blit(detection_img, detection_rect)

            pygame.display.flip()
        pygame.quit()

    def play_explosion(self, screen, image, image_rect, frames):
        """Explosion-Animation abspielen und Hauptbild erst nach dem vorletzten Frame entfernen."""
        for i, frame in enumerate(frames):
            frame_rect = frame.get_rect(center=image_rect.center)
            screen.fill((0, 0, 0))
            if i < len(frames) - 1:
                screen.blit(image, image_rect)

            screen.blit(frame, frame_rect)
            pygame.display.flip()
            time.sleep(0.1)

    def stop(self):
        self.running = False

    def next_position(self):
        self.command_queue.put("next")

    def set_detection_status(self, status):
        """Setzt den Erkennungsstatus."""
        if status == "success":
            self.command_queue.put("success")
        elif status == "fail":
            self.command_queue.put("fail")
        elif status == "clear":
            self.command_queue.put("clear")

    def get_event(self):
        """Rückmeldungen aus der Event-Queue abrufen."""
        try:
            return self.event_queue.get_nowait()
        except queue.Empty:
            return None

class KeyMouseListener(threading.Thread):
    def __init__(self, output_queue):
        super().__init__()
        self.output_queue = output_queue
        self.stop_event = threading.Event()
        # Windows-API-Funktion GetAsyncKeyState laden
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)

    def run(self):
        while not self.stop_event.is_set():
            new_key = self.get_pressed_key()
            if new_key:
                #print(f"new key for {key_to_change}: {new_key}")
                self.output_queue.put(new_key)

    # Funktion, um Hex-Code der gedrückten Tasten zu prüfen
    def get_pressed_key(self):
        # Warte, bis keine Taste gedrückt wird
        while any(self.user32.GetAsyncKeyState(key_code) & 0x8000 for key_code in range(256)):
            time.sleep(0.05)
        # Warte, bis eine neue Taste gedrückt wird
        while True:
            for key_code in range(256):
                if self.user32.GetAsyncKeyState(key_code) & 0x8000:
                    return hex(key_code)
            time.sleep(0.05)


    def stop(self):
        self.stop_event.set()

class PyCyGun:
    def __init__(self, pnum):
        self.pycygun_run = True
        if pnum == 'p2':
            self.saveforplayer = 'player2'
        else:
            self.saveforplayer = 'player1'

        self.path2configstr = 'CyGunConf.ini'
        self.myconfigparser = configparser.ConfigParser()
        self.myconfigparser.read(self.path2configstr)

        self.frame_width = self.myconfigparser.getint(self.saveforplayer, 'recorded_video_frame_width', fallback=1280)
        self.frame_height  = self.myconfigparser.getint(self.saveforplayer, 'recorded_video_frame_height', fallback=720)
        self.contourAreaLen = self.myconfigparser.getint(self.saveforplayer, 'recognized_contour_area_len', fallback=6000)
        self.mouseOutStile = self.myconfigparser.get(self.saveforplayer, 'mouse_output_style', fallback='ctype_abs') ### none, ctype_abs, ctype_inc
        self.setupCamRange = self.myconfigparser.getint(self.saveforplayer, 'start_setup_camrange', fallback=0)

        raw_inc_reset_pos = self.myconfigparser.get(self.saveforplayer, 'ctypes_incremental_reset_pos', fallback='desktop')
        raw_mouse_res_n_frames_frames = self.myconfigparser.getint(self.saveforplayer, 'ctype_mouse_inc_reset_every_n_missed_frames', fallback=10)
        raw_mouseclick_sleep_dur = self.myconfigparser.getfloat(self.saveforplayer, 'ctypes_mouseclick_sleep_duration', fallback=0.1)
        raw_kbdclick_sleep_dur = self.myconfigparser.getfloat(self.saveforplayer, 'ctypes_keyboard_sleep_duration', fallback=0.1)

        self.user_button_working_style = self.myconfigparser.get(self.saveforplayer, 'firebutton_working_style', fallback='direct')
        self.reload_style = self.myconfigparser.get(self.saveforplayer, 'shoot_offscreen4reload', fallback= 'offscreen')



        self.running_modus = "normal_out"

        #self.user_button_working_style = 'direct'
        # mouseclick möglichkeiten
        # single, direct
        # singleshot - click/wait/release
        # direct - keep pressed till button released

        #self.reload_style = 'offscreen'
        # reload when
        # offscreen, None
        # - shoot out of screen
        # - use other mapped button


        # lade SendUserInputData stuff
        if 'ctype' in self.mouseOutStile:
            self.SendUserInputData = CtypesMouseKeyboard(raw_inc_reset_pos, raw_mouse_res_n_frames_frames, raw_mouseclick_sleep_dur, raw_kbdclick_sleep_dur)
            # lade ctypes incremental mouse setup
            if self.mouseOutStile == 'ctype_inc':
                self.SendUserInputData.ctypes_init_incremental_input()
        else:
            self.SendUserInputData = CtypesMouseKeyboard(raw_inc_reset_pos, raw_mouse_res_n_frames_frames, raw_mouseclick_sleep_dur, raw_kbdclick_sleep_dur)

        # Eckenabtasten Pygame stuff
        self.target_overlay = GetCornerOverlay()
        #self.overlay_shootcounter = 0
        self.rPositionRecorder = PositionRecorder()
        self.calib_image = np.zeros((self.frame_height, self.frame_width), dtype=np.uint8)

        if self.myconfigparser.get('debug', 'show_recorded_video', fallback='False') == 'True':
            self.debug_show_video = True
        else:
            self.debug_show_video = False

        calib_cord_oben_links_x = self.myconfigparser.getint(self.saveforplayer, 'calibdata_oben_links_x', fallback=0)
        calib_cord_oben_rechts_x = self.myconfigparser.getint(self.saveforplayer, 'calibdata_oben_rechts_x', fallback=self.frame_width)
        calib_cord_unten_links_x = self.myconfigparser.getint(self.saveforplayer, 'calibdata_unten_links_x', fallback=0)
        calib_cord_unten_rechts_x = self.myconfigparser.getint(self.saveforplayer, 'calibdata_unten_rechts_x', fallback=self.frame_width)
        calib_cord_oben_links_y = self.myconfigparser.getint(self.saveforplayer, 'calibdata_oben_links_y', fallback=0)
        calib_cord_oben_rechts_y = self.myconfigparser.getint(self.saveforplayer, 'calibdata_oben_rechts_y', fallback=0)
        calib_cord_unten_links_y = self.myconfigparser.getint(self.saveforplayer, 'calibdata_unten_links_y', fallback=self.frame_height)
        calib_cord_unten_rechts_y = self.myconfigparser.getint(self.saveforplayer, 'calibdata_unten_rechts_y', fallback=self.frame_height)


         # Kalibrierungsdaten: Ecken des Monitors im Kamerabild
        # Diese Punkte müssen manuell durch Kalibrierung festgelegt werden
        self.camera_points = np.array([
            [calib_cord_oben_links_x, calib_cord_oben_links_y],  # Oben links
            [calib_cord_oben_rechts_x, calib_cord_oben_rechts_y],  # Oben rechts
            [calib_cord_unten_rechts_x, calib_cord_unten_rechts_y],  # Unten rechts
            [calib_cord_unten_links_x, calib_cord_unten_links_y]    # Unten links
        ], dtype=np.float32)

        ##backup:
        # self.camera_points = np.array([
            # [300, 200],  # Oben links
            # [950, 170],  # Oben rechts
            # [930, 520],  # Unten rechts
            # [330, 520]    # Unten links
        # ], dtype=np.float32)

        # Tatsächliche Monitor-Eckpunkte in Bildschirmkoordinaten
        user32 = ctypes.windll.user32
        screen_width, screen_height = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
        #screen_width, screen_height = pyautogui.size()
        self.screen_points = np.array([
            [0, 0],                              # Oben links
            [screen_width, 0],                   # Oben rechts
            [screen_width, screen_height],       # Unten rechts
            [0, screen_height]                   # Unten links
        ], dtype=np.float32)

        # Berechne die Homographie-Matrix
        self.homography_matrix, _ = cv2.findHomography(self.camera_points, self.screen_points)


        # Enable serial connection to arduino
        # get com port
        got_vid = self.myconfigparser.get(self.saveforplayer, 'arduino_vid', fallback='None')
        got_pid = self.myconfigparser.get(self.saveforplayer, 'arduino_pid', fallback='None')
        ## try to set up connection
        self.got_device = None
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if str(port.vid) == got_vid and str(port.pid) == got_pid:
                self.got_device =  port.device  # Gibt den COM-Port zurück
                if self.test_arduino_device(self.got_device, self.saveforplayer) == False:
                    raise Exception("Error: Cant connect to Arduino.")

        # Mapping: Index -> Key im Dictionary
        self.mapping = {
            0: "key0",
            1: "key1",
            2: "key2",
            3: "key3",
            4: "key4"
        }
        self.serial_input_data_queue = queue.Queue()

        # Erstellen und Starten des Arduino-Readers
        self.arduino_reader = SerialButtonsReading(port=self.got_device, baudrate=9600, mapping=self.mapping, data_queue=self.serial_input_data_queue)
        self.arduino_reader.start()

        # Lade Keymap
        self.keymap_button_fire = self.myconfigparser.get(self.saveforplayer, 'keymapping_button_fire', fallback='0x1')
        self.keymap_button_reload = self.myconfigparser.get(self.saveforplayer, 'keymapping_button_reload', fallback='0x2')
        self.keymap_button_opt1 = self.myconfigparser.get(self.saveforplayer, 'keymapping_button_opt1', fallback='0x2')
        self.keymap_button_opt2 = self.myconfigparser.get(self.saveforplayer, 'keymapping_button_opt2', fallback='0x00')
        self.keymap_button_opt3 = self.myconfigparser.get(self.saveforplayer, 'keymapping_button_opt3', fallback='0x00')
        self.keymap_button_opt4 = self.myconfigparser.get(self.saveforplayer, 'keymapping_button_opt4', fallback='0x00')
        self.keymap_button_startsync = self.myconfigparser.get(self.saveforplayer, 'keymapping_button_startsync', fallback='0x00')

        # Lade Key listener
        self.read_user_input_queue = queue.Queue()
        self.keyb_and_mouse_listener_thread = KeyMouseListener(self.read_user_input_queue)
        self.keyb_and_mouse_listener_thread.start()

        # Kamera Setup
        got_picamname = self.myconfigparser.get(self.saveforplayer, 'camera_name', fallback='None')

        graph = FilterGraph()
        allcameras = graph.get_input_devices()
        camID = -1
        for cam in allcameras:
            if got_picamname == cam:
                camID = allcameras.index(cam)
                break

        self.cap = cv2.VideoCapture(camID, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        if not self.cap.isOpened():
            raise Exception("Error! cant open camera with this settings!")







    def test_arduino_device(self, port_name, playernum):
        if playernum == 'player2':
            expected_response = "Lightgun_Arduino_2"
        else:
            expected_response = "Lightgun_Arduino_1"

        try:
            with serial.Serial(port_name, baudrate=9600, timeout=2) as ser:
                time.sleep(1)

                ser.reset_input_buffer()
                ser.reset_output_buffer()

                #catch starting R
                response = ser.readline().decode('utf-8').strip()
                if "RRRRR" in response:
                    ser.write(("get ID\n").encode('utf-8'))
                    response = ser.readline().decode('utf-8').strip()

                if response == expected_response:
                    return True
                else:
                    print(f"Wrong Arduino selected? {port_name}. got answer: {response}")
                    return False
        except Exception as e:
            print(f"Connection error at {port_name}: {e}")
            return False


    def write_config_to_file(self, confsection, confname, confvalue):
        self.myconfigparser.read('CyGunConf.ini')
        self.myconfigparser.set(confsection,confname, str(confvalue))
        with open(self.path2configstr, 'w') as updtini:
            self.myconfigparser.write(updtini)


    def sort_corners(self, corners):
        corners = sorted(corners, key=lambda x: (x[1], x[0]))  # Sortiere nach y, dann nach x
        top_two = sorted(corners[:2], key=lambda x: x[0])  # Obere zwei Punkte
        bottom_two = sorted(corners[2:], key=lambda x: x[0])  # Untere zwei Punkte
        return np.array([top_two[0], top_two[1], bottom_two[1], bottom_two[0]])

    def calculate_angles(self, corners):
        angles = []
        for i in range(len(corners)):
            p1 = corners[i]
            p2 = corners[(i + 1) % len(corners)]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            angle = np.degrees(np.arctan2(dy, dx))  # Winkel in Grad
            angles.append(angle)
        return angles

    def calculate_center(self, corners):
        center_x = np.mean(corners[:, 0])
        center_y = np.mean(corners[:, 1])
        return int(center_x), int(center_y)

    def find_square_corners(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        flipBoth = cv2.flip(gray, -1)
        blurred = cv2.GaussianBlur(flipBoth, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            if len(approx) == 4:
                area = cv2.contourArea(approx)
                if area > self.contourAreaLen:
                    corners = approx.reshape(4, 2)  # Eckpunkte extrahieren
                    corners = self.sort_corners(corners)
                    center_x, center_y = self.calculate_center(corners)

                    ### Calculate deviation
                    frame_center_x = frame.shape[1] // 2
                    frame_center_y = frame.shape[0] // 2
                    deviation_x = center_x - frame_center_x
                    deviation_y = center_y - frame_center_y

                    if self.debug_show_video == True:
                        cv2.drawContours(frame, [approx], -1, (0, 255, 0), 2)
                        for i, corner in enumerate(corners):
                            x, y = corner
                            cv2.circle(frame, (x, y), 5, (255, 0, 0), -1)
                            cv2.putText(frame, f"P{i}: ({x}, {y})", (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                        angles = self.calculate_angles(corners)
                        for i, angle in enumerate(angles):
                            cv2.putText(frame, f"Angle{i}: {angle:.2f}°", (10, 30 + i * 20),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

                        cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
                        cv2.putText(frame, f"Center: ({center_x}, {center_y})", (center_x + 10, center_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                        # cv2.putText(frame, f"Deviation: ({deviation_x}, {deviation_y})", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                        # print("Abweichung vom Bildzentrum:", (deviation_x, deviation_y))

                    return corners, (center_x, center_y), (deviation_x, deviation_y)

        return None, None, None

    def map_to_screen_with_homography(self, point, homography_matrix):
        # Wende die Homographie-Transformation an
        transformed_point = cv2.perspectiveTransform(np.array([[point]], dtype=np.float32), self.homography_matrix)
        return transformed_point[0][0].astype(int)


    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Error  webcam- got no frame.")
            return None

        corners, center, deviation = self.find_square_corners(frame)

        ### get button key input
        keyinput_fire = 0
        key_raw_input_data = None
        if not self.serial_input_data_queue.empty():
            key_raw_input_data = self.serial_input_data_queue.get()
            # print(f"Empfangene Daten: {key_raw_input_data}")
            ## keyinput_fire only for setup corners
            if key_raw_input_data['key0'] == 'P':
                keyinput_fire = 1
                #print("Set keyinputfire to 1")

            ## fire mapped Values



        ### If sync corner is active
        if self.running_modus == "setup_corners":
            if self.setupCamRange == 0:
                self.target_overlay.start()
                #pygame.mouse.set_visible(False) # Hide cursor here
                self.setupCamRange = 1
            elif self.setupCamRange == 1:
                if keyinput_fire == 1:
                    self.target_overlay.next_position()
                    self.setupCamRange = 2
            elif self.setupCamRange == 2:
                if keyinput_fire == 1 and corners is not None:
                    self.rPositionRecorder.add_position(center[0], center[1])
                    self.target_overlay.next_position()
                    self.setupCamRange = 3
            elif self.setupCamRange == 3:
                if keyinput_fire == 1 and corners is not None:
                    self.rPositionRecorder.add_position(center[0], center[1])
                    self.target_overlay.next_position()
                    self.setupCamRange = 4
            elif self.setupCamRange == 4:
                if keyinput_fire == 1 and corners is not None:
                    self.rPositionRecorder.add_position(center[0], center[1])
                    self.target_overlay.next_position()
                    self.setupCamRange = 5
            elif self.setupCamRange == 5:
                if keyinput_fire == 1 and corners is not None:
                    self.rPositionRecorder.add_position(center[0], center[1])
                    self.target_overlay.next_position()
                    self.setupCamRange = 6

                    ### alle 4 punkte gesichert. jetzt zuweisen und speichern

            elif self.setupCamRange == 6:
                eckpunkte = self.rPositionRecorder.get_eckpunkte()
                self.write_config_to_file(self.saveforplayer, 'calibdata_oben_links_x', eckpunkte['oben_links_x'])
                self.write_config_to_file(self.saveforplayer, 'calibdata_oben_rechts_x', eckpunkte['oben_rechts_x'])
                self.write_config_to_file(self.saveforplayer, 'calibdata_unten_links_x', eckpunkte['unten_links_x'])
                self.write_config_to_file(self.saveforplayer, 'calibdata_unten_rechts_x', eckpunkte['unten_rechts_x'])
                self.write_config_to_file(self.saveforplayer, 'calibdata_oben_links_y', eckpunkte['oben_links_y'])
                self.write_config_to_file(self.saveforplayer, 'calibdata_oben_rechts_y', eckpunkte['oben_rechts_y'])
                self.write_config_to_file(self.saveforplayer, 'calibdata_unten_links_y', eckpunkte['unten_links_y'])
                self.write_config_to_file(self.saveforplayer, 'calibdata_unten_rechts_y', eckpunkte['unten_rechts_y'])

                self.camera_points = np.array([
                    [eckpunkte['oben_links_x'], eckpunkte['oben_links_y']],  # Oben links
                    [eckpunkte['oben_rechts_x'], eckpunkte['oben_rechts_y']],  # Oben rechts
                    [eckpunkte['unten_rechts_x'], eckpunkte['unten_rechts_y']],  # Unten rechts
                    [eckpunkte['unten_links_x'], eckpunkte['unten_links_y']]    # Unten links
                ], dtype=np.float32)

                # Berechne die Homographie-Matrix
                self.homography_matrix, _ = cv2.findHomography(self.camera_points, self.screen_points)

                #self.overlay_shootcounter = 99
                self.setupCamRange = 7


            if self.setupCamRange >= 1:
                if corners is not None:
                    self.target_overlay.set_detection_status("success")
                else:
                    self.target_overlay.set_detection_status("fail")

                event = self.target_overlay.get_event()
                if event == "animation_complete":
                    pass
                    #self.overlay_shootcounter += 1
                    #print("Animation abgeschlossen, Bild ist an der neuen Position.")

                if self.setupCamRange >= 7:
                    self.target_overlay.stop()
                    self.target_overlay.join()
                    self.setupCamRange = 0
                    #self.overlay_shootcounter = 0
                    #pygame.mouse.set_visible(True)
                    self.running_modus = "normal_out"



        if self.running_modus == "normal_out":

            if self.mouseOutStile == "ctype_inc" and corners is None:
                self.SendUserInputData.ctype_inc_mouse_position_reset()

            if corners is not None:
                if self.mouseOutStile == "ctype_abs":
                    ### Absolute Eingabe
                    #print(f" Centerpositon: {center[0]}x{center[1]}")
                    screen_x, screen_y = self.map_to_screen_with_homography((center[0], center[1]), self.homography_matrix)
                    #print(f" screenxy: {screen_x}x{screen_y}")
                    self.SendUserInputData.ctype_set_mouse_pos_abs(screen_x, screen_y)

                if self.mouseOutStile == "ctype_inc":
                    ### Absolute Eingabe
                    screen_x, screen_y = self.map_to_screen_with_homography((center[0], center[1]), self.homography_matrix)
                    self.SendUserInputData.ctype_set_mouse_pos_inc(screen_x, screen_y)


        ### erst Bewegung dann Klicks /Eingaben absetzen


        if key_raw_input_data is not None:

            if 'ctype' in self.mouseOutStile:
                # used to reload if gun out of screen
                if self.reload_style == 'offscreen':
                    if corners is None:
                        if self.user_button_working_style == 'direct':
                            self.ctypes_keybind_set_direct_click(key_raw_input_data['key0'], self.keymap_button_reload)
                        elif self.user_button_working_style == 'single':
                            self.ctypes_keybind_set_full_click(key_raw_input_data['key0'], self.keymap_button_reload)

                # if position on screen is detected... do firebutton let fire
                if corners is not None:

                    if self.user_button_working_style == 'direct':
                        self.ctypes_keybind_set_direct_click(key_raw_input_data['key0'], self.keymap_button_fire)
                    elif self.user_button_working_style == 'single':
                        self.ctypes_keybind_set_full_click(key_raw_input_data['key0'], self.keymap_button_fire)

                # do for option buttons
                if self.user_button_working_style == 'direct':
                    self.ctypes_keybind_set_direct_click(key_raw_input_data['key1'], self.keymap_button_opt1)
                    self.ctypes_keybind_set_direct_click(key_raw_input_data['key2'], self.keymap_button_opt2)
                    self.ctypes_keybind_set_direct_click(key_raw_input_data['key3'], self.keymap_button_opt3)
                    self.ctypes_keybind_set_direct_click(key_raw_input_data['key4'], self.keymap_button_opt4)
                elif self.user_button_working_style == 'single':
                    self.ctypes_keybind_set_full_click(key_raw_input_data['key1'], self.keymap_button_opt1)
                    self.ctypes_keybind_set_full_click(key_raw_input_data['key2'], self.keymap_button_opt2)
                    self.ctypes_keybind_set_full_click(key_raw_input_data['key3'], self.keymap_button_opt3)
                    self.ctypes_keybind_set_full_click(key_raw_input_data['key4'], self.keymap_button_opt4)

        user_input_data = None
        if not self.read_user_input_queue.empty():
            user_input_data = self.read_user_input_queue.get()
        if user_input_data != None:
            # print(f" Userdata_got: {user_input_data}")
            in_value = int(user_input_data, 16)
            is_value = int(self.keymap_button_startsync, 16)
            if in_value == is_value:
                self.setupCamRange = 0
                self.running_modus = "setup_corners"





        if self.debug_show_video == True:
            cv2.imshow('CyGun -Debug-', frame)
        return frame


    def ctypes_keybind_set_full_click(self, testbutton, workbutton):
        if workbutton == '0x1':
            if testbutton == 'P':
                self.SendUserInputData.ctypes_mouse_left_click_full()
        elif workbutton == '0x2':
            if testbutton == 'P':
                self.SendUserInputData.ctypes_mouse_right_click_full()
        else:
            if testbutton == 'P':
                self.SendUserInputData.ctypes_pressandrelease_key(workbutton)

    def ctypes_keybind_set_direct_click(self, testbutton, workbutton):
        if workbutton == '0x1':
            if testbutton == 'P':
                self.SendUserInputData.ctypes_mouse_left_click_press()
            elif testbutton == 'R':
                self.SendUserInputData.ctypes_mouse_left_click_release()
        elif workbutton == '0x2':
            if testbutton == 'P':
                self.SendUserInputData.ctypes_mouse_right_click_press()
            elif testbutton == 'R':
                self.SendUserInputData.ctypes_mouse_right_click_release()
        else:
            if testbutton == 'P':
                self.SendUserInputData.ctypes_input_keyboard_key_press(workbutton)
            elif testbutton == 'R':
                self.SendUserInputData.ctypes_input_keyboard_key_release(workbutton)


    def run(self):
        while self.pycygun_run == True:
            frame = self.process_frame()
            if frame is None:
                self.pycygun_run = False

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.pycygun_run = False


        if self.mouseOutStile == 'ctype_inc':
            self.SendUserInputData.ctypes_reset_incremental_input()

        self.cap.release()
        self.arduino_reader.stop()
        self.keyb_and_mouse_listener_thread.stop()
        try:
            cv2.destroyAllWindows()
        except:
            pass

        try:
            self.target_overlay.stop()
        except:
            pass





if __name__ == "__main__":
    if len(sys.argv) == 2:
        playernumber = sys.argv[1]
    else:
        playernumber = 'p1'


    cygun = PyCyGun(playernumber)
    cygun.run()









