import serial
import serial.tools.list_ports
import os, sys
import msvcrt
import time
import configparser

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

def get_initial_values(playernumber):
    print("searching COM ports...")
    ports = serial.tools.list_ports.comports()
    #cnt = 0
    #portlist = []
    for port in ports:
        print(f" {ports.index(port)}  = {port.device}  #  {port.description}")
        #cnt += 1

    print()
    usrinput = int(input("Enter select number for Arduino COM Port:"))
    test_user_input(usrinput)
    if 0 <= usrinput < len(ports):
        print(f"You selected: {ports[usrinput].description}")
        print()
        print("--- Hardware details:")
        print(f"Name (COM-port): {ports[usrinput].device}")          # Der COM-Port (z.B., "COM3")
        print(f"Description: {ports[usrinput].description}")       # Beschreibung des Geräts
        print(f"HWID: {ports[usrinput].hwid}")                      # Hardware-ID (inkl. VID, PID)

        # Extrahiere VID und PID (falls vorhanden)
        if ports[usrinput].vid and ports[usrinput].pid:
            print(f"VID: {ports[usrinput].vid:04X}")                # Vendor ID
            print(f"PID: {ports[usrinput].pid:04X}")                # Product ID

        # Seriennummer (falls vorhanden)
        if ports[usrinput].serial_number:
            print(f"Serial number: {ports[usrinput].serial_number}")

        # Herstellerinformationen (falls vorhanden)
        if ports[usrinput].manufacturer:
            print(f"Manufacturer: {ports[usrinput].manufacturer}")

        print("-" * 40)
        print()
        print("Press any key to continue...")
        msvcrt.getch()
        clear_gui()
        print("now start connection test...")
        res = test_device(ports[usrinput].device, playernumber)
        if res == False:
            print("exiting...")
            time.sleep(1)
            exit()
        else:
            newvid = ports[usrinput].vid
            newpid = ports[usrinput].pid
            newname = ports[usrinput].description
            thesave = write_to_ini(newname, newvid, newpid, playernumber)
            if thesave == False:
                print("exiting...")
                time.sleep(1)
                exit()
            else:
                print("Done! Settings saved.")
                time.sleep(2)
                exit()

    else:
        cnt = len(ports) - 1
        print(f"Wrong input! Must be a number between 0 and {cnt}. Closing...")
        exit()


def test_device(port_name, playernum):
    if playernum == 'p2':
        expected_response = "Lightgun_Arduino_2"
    else:
        expected_response = "Lightgun_Arduino_1"

    try:
        with serial.Serial(port_name, baudrate=9600, timeout=2) as ser:
            time.sleep(2)

            ser.reset_input_buffer()
            ser.reset_output_buffer()

            #catch starting R
            response = ser.readline().decode('utf-8').strip()
            if "RRRRR" in response:
                ser.write(("get ID\n").encode('utf-8'))
                response = ser.readline().decode('utf-8').strip()

            if response == expected_response:
                print(f"Connection established! {port_name}. Saving settings!")
                return True
            else:
                print(f"Wrong Arduino selected? {port_name}. got answer: {response}")
                return False
    except Exception as e:
        print(f"Connection error at {port_name}: {e}")
        return False



def write_to_ini(newname, newvid, newpid, pnum):
    try:
        path2configstr = 'CyGunConf.ini'
        myconfigparser = configparser.ConfigParser()
        myconfigparser.read(path2configstr)
        if pnum == 'p2':
            saveforplayer = 'player2'
        else:
            saveforplayer = 'player1'

        myconfigparser.set(saveforplayer, 'arduino_hw_name', str(newname))
        myconfigparser.set(saveforplayer, 'arduino_pid', str(newpid))
        myconfigparser.set(saveforplayer, 'arduino_vid', str(newvid))

        with open(path2configstr, 'w') as updtini:
            myconfigparser.write(updtini)
    except Exception as e:
        print(f"Error occured while writing ini file. Error: {e}")
        return False

    return True




####
def get_arduino_com_port(pnum):
    path2configstr = 'CyGunConf.ini'
    myconfigparser = configparser.ConfigParser()
    myconfigparser.read(path2configstr)
    if pnum == 'p2':
        saveforplayer = 'player2'
    else:
        saveforplayer = 'player1'

    got_vid = self.myconfigparser.get(saveforplayer, 'arduino_vid', fallback='None')
    got_pid = self.myconfigparser.get(saveforplayer, 'arduino_pid', fallback='None')

    got_device = None
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.vid == got_vid and port.pid == got_pid:
            got_device =  port.device  # Gibt den COM-Port zurück
            if test_device(got_device, pnum) == False:
                return None
    return got_device












if __name__ == "__main__":
    if len(sys.argv) == 2:
        playernumber = sys.argv[1]
    else:
        playernumber = 'p1'

    clear_gui()
    get_initial_values(playernumber)



