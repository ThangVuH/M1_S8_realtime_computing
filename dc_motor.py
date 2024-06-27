import time
from pymata4 import pymata4
import sys
import math
class DC_motor:
    def __init__(self, board=None, pot_pin=0, pos_pin=1, pwm_pin=5, DIR1_pin=8, DIR2_pin=7, poll_time=0.5):
        self.board = board
        self.pot_pin = pot_pin
        self.pos_pin = pos_pin
        self.pwm_pin = pwm_pin
        self.DIR1_pin = DIR1_pin
        self.DIR2_pin = DIR2_pin
        self.poll_time = poll_time
        self.kp_position = 20
        self.kp_velocity = 0.5
        self.target_position = 0
        self.current_position = 0


        # Initialize sensors and actuators
        self.board.set_pin_mode_analog_input(self.pot_pin)
        self.board.set_pin_mode_analog_input(self.pos_pin)
        self.board.set_pin_mode_pwm_output(self.pwm_pin)
        self.board.set_pin_mode_digital_output(self.DIR1_pin)
        self.board.set_pin_mode_digital_output(self.DIR2_pin)

        self.value = self.board.analog_read(self.pot_pin)
        self.time = self.value[1]

    def control_velocity(self, target_velocity):
        pwm_value = int(self.kp_velocity * target_velocity)
        self.board.digital_write(self.DIR1_pin, 1)
        self.board.digital_write(self.DIR2_pin, 0)
        self.board.pwm_write(self.pwm_pin, min(max(pwm_value, 0), 255))




    def update_positions(self):
        self.target_position,self.time = (self.board.analog_read(self.pot_pin)[0] / 1024) * 255, self.board.analog_read(self.pot_pin)[1]
        self.current_position = (self.board.analog_read(self.pos_pin)[0] / 1024) * 255


    def control_position(self):
        self.update_positions()


        final_error = min([(self.target_position - self.current_position + angle) for angle in [-2*math.pi, 0, 2*math.pi]], key=abs)
        abserror = abs(final_error)
        print(f"final error: {final_error}")
        control_effort = int(self.kp_position * (abserror / 2 if abserror <= 10 else abserror))         
        # less_error_sleep_time = self.poll_time + max(0, (1 - abserror/255)) * 3  # Increase up to 2 seconds
        direction = 1 if final_error <= 0 else 0
        self.board.digital_write(self.DIR1_pin, direction > 0)
        self.board.digital_write(self.DIR2_pin, direction <= 0)


        self.board.pwm_write(self.pwm_pin, min(control_effort, 255))


        # time.sleep(less_error_sleep_time)
        time.sleep(self.poll_time)
   
    def stop_motor(self):
        self.board.digital_write(self.DIR1_pin, 0)
        self.board.digital_write(self.DIR2_pin, 0)
        self.board.pwm_write(self.pwm_pin, 0)
        print("\nMotor stopped.")
        sys.exit(0)


if __name__ == '__main__':
    board = pymata4.Pymata4()
    motor = DC_motor(board=board)
    try:
        while True:
            motor.control_position()
            print(f"Target: {motor.target_position}, Current: {motor.current_position}, time: {motor.time}")
    except KeyboardInterrupt:
        motor.stop_motor()
        print("Program exited by user.")