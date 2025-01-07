import os, time
from pygrabber.dshow_graph import FilterGraph
import configparser
import cv2
import msvcrt
from multiprocessing import Process, Queue
import pygame
import sys
import ctypes

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

class FrameDetectionSync:
    def __init__(self, pnum):
        self.playernumber = 'player1'
        if pnum == 2:
            self.playernumber = 'player2'

        self.path2configstr = 'CyGunConf.ini'
        self.myconfigparser = configparser.ConfigParser()
        self.myconfigparser.read(self.path2configstr)

        self.frame_width = self.myconfigparser.getint(self.playernumber, 'recorded_video_frame_width', fallback=1280)
        self.frame_height  = self.myconfigparser.getint(self.playernumber, 'recorded_video_frame_height', fallback=720)
        self.camera_name = self.myconfigparser.get(self.playernumber, 'camera_name', fallback='None')
        self.camera_id = 0
        if self.camera_name != 'None':
            graph = FilterGraph()
            allcameras = graph.get_input_devices()
            self.camera_id = allcameras.index(self.camera_name)

        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        if not self.cap.isOpened():
            raise Exception("Error! Could not open webcam.")
        self.est_contourAreaLen = 0

        pygame.init()

        # info = pygame.display.Info()
        # self.screen_width = info.current_w
        # self.screen_height = info.current_h

        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        self.screen_width, self.screen_height = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)

        self.aspect_ratio = self.screen_width / self.screen_height
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.rect_width = 10
        self.rect_height = int(self.rect_width / self.aspect_ratio)

        self.center_x = self.screen_width // 2
        self.center_y = self.screen_height // 2
        self.clock = pygame.time.Clock()
        self.running = True
        self.runstatus = 0
        self.runcounter = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False

    def update_growing(self, pixel):
        self.rect_width += pixel
        self.rect_height = int(self.rect_width / self.aspect_ratio)

    def draw_growing(self):
        rect = pygame.Rect(
            self.center_x - self.rect_width // 2,
            self.center_y - self.rect_height // 2,
            self.rect_width,
            self.rect_height
        )

        self.screen.fill(self.BLACK)
        pygame.draw.rect(self.screen, self.WHITE, rect)
        pygame.display.flip()


    def run(self):
        while self.running:
            self.handle_events()
            if self.runstatus == 0:
                self.update_growing(2)
                self.draw_growing()
                self.process_frame()

                if self.rect_width >= self.screen_width and self.rect_height >= self.screen_height:
                    self.runcounter += 1
                    if self.runcounter >= 60:
                        self.runstatus = 1
                        self.runcounter = 0
                        self.rect_width = 10
                        self.rect_height = int(self.rect_width / self.aspect_ratio)
            elif self.runstatus == 1:
                rwn = self.est_contourAreaLen * 0.9
                rwn = int(rwn)
                self.write_config_to_file(self.playernumber, 'recognized_contour_area_len', rwn)
                self.running = False

            self.clock.tick(60)

        self.quit()

    def quit(self):
        print(f"estimated contour area lenght: {self.est_contourAreaLen}")
        self.cap.release()
        pygame.quit()

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Error! No picture from cam retrieved.")
            return

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
                if area > self.est_contourAreaLen:
                    self.est_contourAreaLen = area

    def write_config_to_file(self, confsection, confname, confvalue):
        self.myconfigparser.read('CyGunConf.ini')
        self.myconfigparser.set(confsection,confname, str(confvalue))
        with open(self.path2configstr, 'w') as updtini:
            self.myconfigparser.write(updtini)


if __name__ == "__main__":
    clear_gui()
    print("Sync your cam with your monitor/display for frame detection")
    print()
    if len(sys.argv) == 2:
        playernumber = sys.argv[1]
    else:
        playernumber = 'p1'

    if playernumber == 'p2':
        syncplayer = 2
    else:
        syncplayer = 1
    #print("Now type 1 to start setup of player one camera or 2 for player two")
    #syncplayer = int(input("Player:"))
    test_user_input(syncplayer)

    print()
    wot = '''
    Please set up the lightgun now so that it is in the same position
    as if you wanted to shoot at the center of the screen later.
    The camera must capture the entire screen.
    When you press any key, a full screen animation starts and the synchronization begins.

    Please do not move the camera during the process.
    '''
    print(wot)
    print("Press any key to continue...")
    msvcrt.getch()
    print("Continuing...")

    app = FrameDetectionSync(syncplayer)
    app.run()




