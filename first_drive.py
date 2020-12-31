import time

from evdev import InputDevice, categorize, ecodes
import gpiozero
import numpy as np

controller = InputDevice('/dev/input/event0')

buttons = {
    307: 'x',
    308: 'y',
    305: 'b',
    304: 'a',
    310: 'lb',
    311: 'rb',
    315: 'menu',
    158: 'screen'
    }

joysticks = {
    0: 'lj-x',
    1: 'lj-y',
    2: 'rj-x',
    5: 'rj-y',
    9: 'rt',
    10: 'lt'
    }

front_left = gpiozero.Motor(7,8)
front_right = gpiozero.Motor(9,10)

def check_for_stop(btn=315):
    if btn in controller.active_keys():
        return True

def check_for_drive():
    # Get commands
    y_pos = controller.absinfo(1)
    x_pos = controller.absinfo(0)

    # Convert to speeds
    front_to_back = float(np.interp(y_pos.value / 1000, [0, 65], [1, -1]))
    side_to_side = float(np.interp(x_pos.value / 1000, [0, 65], [1, -1]))

    if side_to_side > 0:  # Commanding left
        right = front_to_back
        left = front_to_back *  np.interp(side_to_side, [0, 1], [1, -1])
    else:  # Commanding right
        right = front_to_back * np.interp(abs(side_to_side), [0, 1], [1, -1])
        left = front_to_back

    return right, left

def command_drive(right, left):

    if right >= 0:
        front_right.forward(right)
    else:
        front_right.backward(-right)

    if left >= 0:
        front_left.forward(left)
    else:
        front_left.backward(-left)

def run_loop():
    while(True):
        # Check for stop
        if check_for_stop():
            break

        # Check for drive
        fwd, lft = check_for_drive()

        # Command robot
        command_drive(fwd, lft)

        # Wait for next loop
        time.sleep(0.5)

if __name__ == '__main__':
    run_loop()
