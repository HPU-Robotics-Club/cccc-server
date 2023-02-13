from flask import Flask, request
from serial_communicator import SerialCommunicator, MotorCode

app = Flask(__name__)
serial = SerialCommunicator()

@app.route('/')
def example():
    json = request.get_json()

    controller_x = json["controller_x"]
    controller_y = json["controller_y"]

    #print(f'x = {x}')
    #print(f'y = {y}')

    leftSpeed = 0
    rightSpeed = 0
    # Parses raw controller values
    if abs(controller_x) > 0.1 or abs(controller_y) > 0.1:
        # Acquires the sign of x and y
        ySine = abs(controller_y)/controller_y if controller_y != 0 else 1
        xSine = abs(controller_x)/controller_x if controller_x != 0 else 1

        if abs(controller_x) <= 0.5:
            leftSpeed = controller_y * 127 + ySine * 128
            rightSpeed = leftSpeed
        else:
            leftSpeed = controller_x * 127 + xSine * 128
            rightSpeed = -leftSpeed

    return parseAndSendMotorCode(leftSpeed, rightSpeed, serial)

def parseAndSendMotorCode(leftSpeed: int, rightSpeed: int, serial):
    leftSpeed = round(leftSpeed) if abs(leftSpeed) > 30 else 0
    rightSpeed = round(rightSpeed) if abs(rightSpeed) > 30 else 0
    # print(f'leftSpeed = {leftSpeed}, rightSpeed = {rightSpeed}')
    left_motor_code = MotorCode.WHEELS_FORWARD if leftSpeed >= 0 else MotorCode.WHEELS_BACKWARD
    right_motor_code = MotorCode.WHEELS_FORWARD if rightSpeed >= 0 else MotorCode.WHEELS_BACKWARD
    return serial.write_motor_command(left_motor_code, right_motor_code, abs(leftSpeed), abs(rightSpeed))

if __name__ == '__main__':
    app.run
    app.run(host="0.0.0.0", port=5000)