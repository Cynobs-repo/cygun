import ctypes
import time
import configparser
import msvcrt
import os, sys


def clear_gui():
    os.system('cls' if os.name == 'nt' else 'clear')

# Windows-API-Funktion GetAsyncKeyState laden
user32 = ctypes.WinDLL('user32', use_last_error=True)

# Funktion, um Hex-Code der gedrückten Tasten zu prüfen
def get_pressed_key():
    # Warte, bis keine Taste gedrückt wird
    while any(user32.GetAsyncKeyState(key_code) & 0x8000 for key_code in range(256)):
        time.sleep(0.05)
    # Warte, bis eine neue Taste gedrückt wird
    while True:
        for key_code in range(256):
            if user32.GetAsyncKeyState(key_code) & 0x8000:
                return hex(key_code)
        time.sleep(0.05)


# Config-Datei-Verwaltung
CONFIG_FILE = "CyGunConf.ini"
def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config

def save_config(config):
    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)

def wait_for_input(prompt):
    print(prompt, end='', flush=True)
    while True:
        if msvcrt.kbhit():  # Warte auf eine Tasteneingabe
            char = msvcrt.getch().decode('utf-8', errors='ignore')  # Zeichen erfassen
            print(char)  # Zeichen anzeigen
            return char


def main(player2save):
    # Laden der vorhandenen oder Standard-Tastenbelegungen
    config = load_config()
    key_mapping = {
        "keymapping_button_fire": config.get(player2save, "keymapping_button_fire", fallback="0x00"),
        "keymapping_button_reload": config.get(player2save, "keymapping_button_reload", fallback="0x00"),
        "keymapping_button_startsync": config.get(player2save, "keymapping_button_startsync", fallback="0x00"),
        "keymapping_button_opt1": config.get(player2save, "keymapping_button_opt1", fallback="0x00"),
        "keymapping_button_opt2": config.get(player2save, "keymapping_button_opt2", fallback="0x00"),
        "keymapping_button_opt3": config.get(player2save, "keymapping_button_opt3", fallback="0x00"),
        "keymapping_button_opt4": config.get(player2save, "keymapping_button_opt4", fallback="0x00"),
    }

    while True:
        clear_gui()
        print("Keymapping for CyGun:")
        print()
        for key, value in key_mapping.items():
            print(f"{key[18:]}:   {value}")
        print()
        print()
        print("Options:")
        print("1: change mapping")
        print("2: save and exit")
        print("3: exit")

        choice = wait_for_input("please choose: ")
        clear_gui()
        if choice == "1":
            print()
            print("Which button do you like to change?")
            print()
            for i, key in enumerate(key_mapping.keys(), start=1):
                print(f"{i}: {key[18:]}")
            print()
            selected = wait_for_input("select: ")

            if selected.isdigit() and 1 <= int(selected) <= len(key_mapping):
                key_to_change = list(key_mapping.keys())[int(selected) - 1]
                print(f"Now press the key for {key_to_change}...")

                while True:
                    new_key = get_pressed_key()
                    if new_key:
                        key_mapping[key_to_change] = new_key
                        print(f"new key for {key_to_change}: {new_key}")
                        break
                    time.sleep(0.1)
        elif choice == "2":
            for key, value in key_mapping.items():
                config.set(player2save, key, value)
            save_config(config)
            print("Button mapping saved! Closing.")
            break
        elif choice == "3":
            exit()
        else:
            print("Wrong selection. Try again.")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        playernumber = sys.argv[1]
    else:
        playernumber = 'p1'

    if playernumber == 'p2':
        player2save = 'player2'
    else:
        player2save = 'player1'
    main(player2save)
