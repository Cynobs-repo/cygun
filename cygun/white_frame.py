import pygame
import ctypes
import win32api, win32gui, win32con
import threading
import time
import configparser
import lightgunicon
import base64
import io

def bring_window_to_front():
    while True:
        time.sleep(1)
        ismin = int(ctypes.windll.user32.IsIconic(hwnd))
        if ismin == 1:
            #ctypes.windll.user32.ShowWindow(hwnd, 9)  # 9 entspricht SW_RESTORE
            win32gui.ShowWindow(hwnd, 9)

        actual_topmost = win32gui.GetForegroundWindow()
        if actual_topmost != hwnd:
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE)
            win32gui.ShowWindow(hwnd, 9)


class Point(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_int),
    ]
    def __eq__(self, other):
        return (self.x == other.x)
    def __ne__(self, other):
        return not self.__eq__(other)


def get_all_windows():

    def enum_handler(hwnd, results):
        window_placement = win32gui.GetWindowPlacement(hwnd)
        results.append({
            "hwnd":hwnd,
            "hwnd_above":win32gui.GetWindow(hwnd, win32con.GW_HWNDPREV), # Window handle to above window
            "title":win32gui.GetWindowText(hwnd),
            "visible":win32gui.IsWindowVisible(hwnd) == 1,
            "minimized":window_placement[1] == win32con.SW_SHOWMINIMIZED,
            "maximized":window_placement[1] == win32con.SW_SHOWMAXIMIZED,
            "rectangle":win32gui.GetWindowRect(hwnd) #(left, top, right, bottom)
        })

    enumerated_windows = []
    try:
        win32gui.EnumWindows(enum_handler, enumerated_windows)
    except:
        print("Error in get_all_Windows func")
    finally:
        return enumerated_windows


def get_visible_windows():
    visibleWindows = []
    windows = get_all_windows()

    for window in windows:
        try:
            if window["title"] == "" or not window["visible"] or window["minimized"]:
                continue
            if window["hwnd"] == hwnd:
                continue

            ### Windows "Program Manager" fuck it up. It does like its fullscreen but its not visible
            ### Check for class name progmen - if th window is from there > skip it.
            buffer = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetClassNameW(window["hwnd"], buffer, 256)
            class_name = buffer.value
            #print(class_name)
            if class_name == "Progman":
                continue

            isCloaked = ctypes.c_int(0)
            tst = ctypes.c_int(0)
            ctypes.WinDLL("dwmapi").DwmGetWindowAttribute(window["hwnd"], 14, ctypes.byref(isCloaked), ctypes.sizeof(isCloaked))
            p1 = Point(isCloaked)
            p2 = Point(tst)
            if p1 == p2:
                visibleWindows.append(window)
        except Exception as error:
            print("Error Single Part in get_visible_windows func")
            print("An exception occurred:", error)

    return visibleWindows

def get_active_window_frames():
    out = []
    gotlist = get_visible_windows()
    for line in gotlist:
        if line["maximized"]:
            out.append(line)
            return out
        else:
            out.append(line)
    return out

def testforfullscreen():
    retval = False
    worksize = getscreenFullSize()
    framelist = get_active_window_frames()
    #print(framelist)
    for part in framelist:
        rect = part['rectangle']
        if rect[0] == 0 and rect[1] == 0 and rect[2] == worksize[0] and rect[3] == worksize[1]:
            #print("switch fullscreen")
            retval = True
    return retval


def getscreenWorkingSize():
    hWnd = ctypes.WinDLL("user32").FindWindowW(u"Shell_traywnd", None)
    window_placement = win32gui.GetWindowPlacement(hWnd)
    window_placement = list(window_placement)
    screensize = []
    screensize.append(window_placement[4][2])
    screensize.append(window_placement[4][1])
    return screensize

def getscreenFullSize():
    user32 = ctypes.windll.user32
    #screensize = user32.GetSystemMetrics(78), user32.GetSystemMetrics(79) # Multi Monitor setup
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1) # single Display Setup
    return screensize


def load_base64_image(base64_data):
        try:
            image_data = base64.b64decode(base64_data)
            image_stream = io.BytesIO(image_data)
            image = pygame.image.load(image_stream, "PNG")
            return image
        except Exception as e:
            print(f"Error loading base64 image: {e}")
            return None

if __name__ == "__main__":
    change_screen_upate_setting = "auto" # auto, static
    if change_screen_upate_setting == "static":
        windows_working_size = getscreenFullSize()
    else:
        windows_working_size = getscreenWorkingSize()

    pygame.init()
    pgm_icon = load_base64_image(lightgunicon.LightgunICON)
    pygame.display.set_icon(pgm_icon)

    path2configstr = 'CyGunConf.ini'
    myconfigparser = configparser.ConfigParser()
    myconfigparser.read(path2configstr)

    screen = pygame.display.set_mode(windows_working_size, pygame.NOFRAME, pygame.RESIZABLE)
    hwnd = pygame.display.get_wm_info()["window"]
    pygame.display.set_caption('CyGun - frame')

    ### #### Programm aus der Taskleiste verschwinden lassen:
    # win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
    # win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_TOOLWINDOW)
    # win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

    ### ### Hintergrund entfernen
    unvisible_color_rgb = (100, 113, 102)
    unvisible_color_rgba = (100, 113, 102, 255)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*unvisible_color_rgb), 0, win32con.LWA_COLORKEY)

    ### ### Fenster dauernd nach vorne holen
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE)
    win32gui.SetForegroundWindow(hwnd)
    win32gui.ShowWindow(hwnd, 9)

    clock = pygame.time.Clock()
    line_color = (255, 255, 255)
    line_thick = myconfigparser.getint("whiteframe", 'frame_boarder_size', fallback=30)


    keep_win_open_thread = threading.Thread(target=bring_window_to_front, daemon=True).start()

    running = True
    start_time = time.time()



    while running:
        #test every n seconds if something went fullscreen
        if change_screen_upate_setting == "auto":
            elapsed_time = time.time() - start_time
            if elapsed_time >= 2:
                if testforfullscreen() == True:
                    newsize = getscreenFullSize()
                    if newsize != windows_working_size:
                        windows_working_size = newsize
                        screen = pygame.display.set_mode(windows_working_size, pygame.NOFRAME, pygame.RESIZABLE)
                else:
                    newsize = getscreenWorkingSize()
                    if newsize != windows_working_size:
                        windows_working_size = newsize
                        screen = pygame.display.set_mode(windows_working_size, pygame.NOFRAME, pygame.RESIZABLE)
                start_time = time.time()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                #time.sleep(1)
                newsize = getscreenFullSize()
                windows_working_size = newsize
                screen = pygame.display.set_mode(windows_working_size, pygame.NOFRAME, pygame.RESIZABLE)
            elif event.type == pygame.ACTIVEEVENT:
                if event.gain == 1:  # Fenster wird wieder aktiv
                    # print("Fenster wurde wiederhergestellt")
                    #time.sleep(1)
                    newsize = getscreenFullSize()
                    windows_working_size = newsize
                    screen = pygame.display.set_mode(windows_working_size, pygame.NOFRAME, pygame.RESIZABLE)


        screen.fill(unvisible_color_rgba)

        pygame.draw.line(screen, line_color, (0, 0), (0, windows_working_size[1]), line_thick)
        pygame.draw.line(screen, line_color, (0, 0), (windows_working_size[0], 0), line_thick)
        pygame.draw.line(screen, line_color, (windows_working_size[0], 0), (windows_working_size[0], windows_working_size[1]), line_thick)
        pygame.draw.line(screen, line_color, (0, windows_working_size[1]), (windows_working_size[0], windows_working_size[1]), line_thick)

        pygame.display.flip()
        clock.tick(5)

    pygame.quit()
