import io
import os
import re
import time
import board
import storage
import usb_hid
import digitalio

from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse

cc = ConsumerControl(usb_hid.devices)
kb = Keyboard(usb_hid.devices)
ms = Mouse(usb_hid.devices)

bt = digitalio.DigitalInOut(board.GP25)
bt.direction = digitalio.Direction.INPUT
bt.pull = digitalio.Pull.UP

led = digitalio.DigitalInOut(board.GP12)
led.direction = digitalio.Direction.OUTPUT
led.value = True

looping = False
loop_pos = 0
loop_count = 0
iteration = 0

#Added aliases for more convenient use 
def keyname(key):
    aliases = {
        "DOWN": "DOWN_ARROW",
        "UP": "UP_ARROW",
        "LEFT": "LEFT_ARROW",
        "RIGHT": "RIGHT_ARROW",
        "PAGEUP": "PAGE_UP",
        "PAGEDOWN": "PAGE_DOWN",
        "CAPSLOCK": "CAPS_LOCK",
        "PRINTSCREEN": "PRINT_SCREEN",
        "CTRL": "CONTROL",
        "WIN":  "GUI",
    }
    return aliases.get(key, key)



#TO DO : expand the macros and centralize them in a dict
def macro_copy():
    kb.send(Keycode.LEFT_CONTROL, Keycode.C)

def macro_paste():
    kb.send(Keycode.LEFT_CONTROL, Keycode.V)

def macro_select_all():
    kb.send(Keycode.LEFT_CONTROL, Keycode.Q)

def macro_save():
    kb.send(Keycode.LEFT_CONTROL, Keycode.S)

MACROS = {
    "COPY": macro_copy,
    "PASTE": macro_paste,
    "SELECTALL": macro_select_all,
    "SAVE": macro_save,
}



def execute_command(function, command):

    #check if a macro is called
    macro_fn = MACROS.get(function)
    if macro_fn:
        macro_fn()
        return
    
    if function == "DELAY":
        if command.isdigit():
            time.sleep(float(command))
    
    elif function == "PRESS":
        command = command.split(" + ")
        for c in range(0, len(command), 1):
            command[c] = keyname(command[c].upper()) #gestion des alias
        if len(command) <= 6:
            keys = [0] * len(command)
            for idx in range(0, len(command), 1):
                keys[idx] = getattr(Keycode, command[idx])
            kb.send(*keys)
    elif function == "WRITE":
        layout.write(command)
    elif function == "HOLD":
        command = command.split(" + ")
        for c in range(0, len(command), 1):
            command[c] = keyname(command[c].upper()) #gestion des alias
        if len(command) <= 6:
            keys = [0] * len(command)
            for idx in range(0, len(command), 1):
                keys[idx] = getattr(Keycode, command[idx])
            kb.press(*keys)
    elif function == "RELEASE":
        kb.release_all()
    elif function == "MOVE":
        command = command.split(", ")
        pos = [0] * 2
        for i in range(0, len(command), 1):
            pos[i] = int(command[i])
        ms.move(x=pos[0], y=-1*pos[1], wheel=0)
    elif function == "SCROLL":
        ms.move(x=0, y=0, wheel=int(command))
    elif function == "CLICK":
        if command == "left":
            ms.click(Mouse.LEFT_BUTTON)
        elif command == "middle":
            ms.click(Mouse.MIDDLE_BUTTON)
        elif command == "right":
            ms.click(Mouse.RIGHT_BUTTON)
    elif function == "VOLUME":
        if command.isdigit():
            for vc in range(0, abs(int(command)), 1):
                if int(command) > 0:
                    cc.send(ConsumerControlCode.VOLUME_INCREMENT)
                elif int(command) < 0:
                    cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        elif command == "mute":
            cc.send(ConsumerControlCode.MUTE)
    

def get_substr(string, start, end):
    command = ""
    for idx in range(start+1, end):
            command += string[idx]
    return command


try:
    file = io.open("/layout.txt", "r")
    line = file.readline()
    command = get_substr(line, line.find("("), line.rfind(")"))
    if command == "US":
        from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
        layout = KeyboardLayoutUS(kb)
    elif command == "CRO":
        from keyboard_layouts.keyboard_layout_win_cr import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "UK":
        from keyboard_layouts.keyboard_layout_win_uk import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "FR":
        from keyboard_layouts.keyboard_layout_win_fr import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "CZ":
        from keyboard_layouts.keyboard_layout_win_cz import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "BR":
        from keyboard_layouts.keyboard_layout_win_br import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "DE":
        from keyboard_layouts.keyboard_layout_win_de import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "ES":
        from keyboard_layouts.keyboard_layout_win_es import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "HU":
        from keyboard_layouts.keyboard_layout_win_hu import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "IT":
        from keyboard_layouts.keyboard_layout_win_it import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "PO":
        from keyboard_layouts.keyboard_layout_win_po import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "SW":
        from keyboard_layouts.keyboard_layout_win_sw import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "TR":
        from keyboard_layouts.keyboard_layout_win_tr import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "BE":
        from keyboard_layouts.keyboard_layout_win_bene import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "SG":
        from keyboard_layouts.keyboard_layout_win_sg import KeyboardLayout
        layout = KeyboardLayout(kb)



    file = io.open("/pico_usb.txt", "r")

    line = file.readline()
    while line != "":
        function = line.split("(",1)[0].upper()
        command = get_substr(line, line.find("("), line.rfind(")"))
        if looping == False:
            loop_pos += len(line)
        if function == "LOOP":
            looping = True
            if command.isdigit():
                command = int(command)
                iteration = command
            else:
                command = -1
                iteration = int(command)


        execute_command(function, command)
        line = file.readline()

    file.close()  
    file = io.open("/pico_usb.txt", "r")



    while looping == True:

        if iteration > 0:
            for _ in range(iteration):
                file.seek(loop_pos)
                line = file.readline()
                while line != "":
                    function = line.split("(",1)[0].upper()
                    command = get_substr(line, line.find("("), line.rfind(")"))
                    execute_command(function, command)
                    line = file.readline()

        elif iteration == -1:  
            file.seek(loop_pos)
            line = file.readline()
            while line != "":
                function = line.split("(",1)[0].upper()
                command = get_substr(line, line.find("("), line.rfind(")"))
                execute_command(function, command)
                line = file.readline()

    file.close()

except OSError as e:
    print(e)
kb.release_all()