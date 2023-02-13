import string
import serial
from enum import Enum

PORT = '/dev/ttyACM0'
DIVIDER = "|"
BAUDRATE = 115200

class SerialCommunicator:
    def __init__(self):
        print("Starting serial communicator...")
        # self.arduino = serial.Serial(PORT, BAUDRATE)
        print("Starting serial communicator...")

        self.prev_left_speed = 0
        self.prev_right_speed = 0

    def write(self, msg: str):
        code = f'{msg}{DIVIDER}'
        # self.arduino.write(code.encode())
        print(f'{code}')
        return code
    
    def write_motor_command(self, left_motor_code: str, right_motor_code: str, left_motor_value: int, right_motor_value: int):
        # This if statement makes it so that it wont send duplicate motor commands right after each other
        if (left_motor_value != self.prev_left_speed or right_motor_value != self.prev_right_speed):
            code = self.write(f'{left_motor_code}{self.format_motor_value(left_motor_value)}{right_motor_code}{self.format_motor_value(right_motor_value)}')
            
            # Assigns current motor values to the previous motor value variables
            self.prev_left_speed = left_motor_value
            self.prev_right_speed = right_motor_value
            return code
        
        return "Duplicate Sent!"

    def format_motor_value(self, motor_value: int):
        N = 0
        if motor_value < 10:
            N = 2
        elif motor_value < 100:
            N = 1
        
        output_str = str(motor_value)
        for i in range(0, N):
            output_str = f'0{output_str}'

        return output_str

class MotorCode():
    WHEELS_FORWARD = "wf"
    WHEELS_BACKWARD = "wb"
