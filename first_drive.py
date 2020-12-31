import time
import math

from evdev import InputDevice, categorize, ecodes
import gpiozero
import numpy as np

from controller import map_controller


class Rover:
    def __init__(self):
        self.controller = InputDevice('/dev/input/event0')
        self.deadspace = 0.1  # 10% controller deadspace

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
        pi = math.pi

        # Get commands
        y_pos = self.controller.absinfo(1)
        x_pos = self.controller.absinfo(0)

        # Convert to speeds
        radius, theta = self._js_pos(x_pos, y_pos)

        if radius > self.deadspace:  # Add dead space for controller error
            if theta <= pi/2:  # Forward right turn
                right = radius * np.interp(theta, [0, pi/4], [-1, 1])
                left = radius
            elif theta <= pi:  # Forward left turn
                right = radius
                left = radius * np.interp(theta, [pi/2, pi], [1, -1])
            elif theta <= 3*pi/2:  # Backwards left turn
                right = radius * np.interp(theta, [pi, 3*pi/2], [1, -1])
                left = - radius
            else:  # Backwards right turn
                right = - radius
                left = radius * np.interp(theta, [3*pi/2, 0], [-1, 1])
        else:
            left = 0
            right = 0

        return right, left

    def command_drive(self, right, left):
        """Command the motors to drive"""

        # Command right motors
        if right >= 0:
            self.front_right.forward(right)
        else:
            self.front_right.backward(-right)

        # Command left motors
        if left >= 0:
            self.front_left.forward(left)
        else:
            self.front_left.backward(-left)

    def run_loop(self):
        """Run loop. Can be exited by button 315 on the controller"""
        while not self.check_for_stop():

            # Check for drive
            fwd, lft = self.check_for_drive()

            # Command robot
            self.command_drive(fwd, lft)

            # Wait for next loop
            time.sleep(0.5)

    @staticmethod
    def _js_pos(x, y):
        """Converts the joystick pos into radius and theta"""
        x_val = np.interp(x.value, [0, x.max], [-1, 1])
        y_val = np.interp(y.value, [0, y.max], [-1, 1])

        radius = np.sqrt(x_val**2 + y_val**2)
        theta = math.acos(y_val/x_val)

        return radius, theta


# Run if main
if __name__ == '__main__':
    rover = Rover()
    rover.run_loop()
