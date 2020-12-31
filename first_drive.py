import time

from evdev import InputDevice, categorize, ecodes
import gpiozero
import numpy as np

from controller import map_controller


class Rover:
    def __init__(self):
        self.controller = InputDevice('/dev/input/event0')

        # Map the controller buttons
        self.buttons, self.jsticks = map_controller()

        # Define motors
        self.front_left = gpiozero.Motor(7, 8)
        self.front_right = gpiozero.Motor(9, 10)
        self.back_left = gpiozero.Motor(17, 18)  # Placeholder
        self.back_right = gpiozero.Motor(19, 20)  # Placeholder

    def check_for_stop(self, btn=315):
        if btn in self.controller.active_keys():
            return True

    def check_for_drive(self):
        # Get commands
        y_pos = self.controller.absinfo(1)
        x_pos = self.controller.absinfo(0)

        # Convert to speeds
        front_to_back = float(np.interp(y_pos.value / 1000, [0, 65], [1, -1]))
        side_to_side = float(np.interp(x_pos.value / 1000, [0, 65], [1, -1]))

        if side_to_side > 0:  # Commanding left
            right = front_to_back
            left = front_to_back * np.interp(side_to_side, [0, 1], [1, -1])
        else:  # Commanding right
            right = front_to_back * np.interp(abs(side_to_side), [0, 1], [1, -1])
            left = front_to_back

        return right, left

    def command_drive(self, right, left):

        if right >= 0:
            self.front_right.forward(right)
        else:
            self.front_right.backward(-right)

        if left >= 0:
            self.front_left.forward(left)
        else:
            self.front_left.backward(-left)

    def run_loop(self):
        while not self.check_for_stop():

            # Check for drive
            fwd, lft = self.check_for_drive()

            # Command robot
            self.command_drive(fwd, lft)

            # Wait for next loop
            time.sleep(0.5)


if __name__ == '__main__':
    rover = Rover()
    rover.run_loop()
