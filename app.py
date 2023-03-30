from flask import Flask, request
from serial_communicator import SerialCommunicator, MotorCode

app = Flask(__name__)
serial = SerialCommunicator()

@app.post('/')
def post_handle():
    json = request.get_json()

    x = json["controller_x"]
    y = json["controller_y"]
    r1 = json["controller_r1"]
    l1 = json["controller_l1"]
    dup = json["constroller_dub"]
    ddown = json["controller_ddown"]

    beltSpeed = 0
    isBeltForward = True
    leftSpeed = 0
    rightSpeed = 0
    actSpeed = 0
    isActForward = True

    useWheels = True

    # Handles right trigger for belt up
    if r1 > 0.1:
        beltSpeed = 127 + r1 * 128
        useWheels = False
    # Handles left trigger for belt down
    elif l1 > 0.1:
        beltSpeed = 127 + l1 * 128
        isBeltForward = False
        useWheels = False

    # Handles dpad for moving the actuator up and down
    if dup is not None:
        actSpeed = 200
        useWheels = False
    elif ddown is not None:
        actSpeed = 200
        isActForward = False
        useWheels = False

    # Handles wheels
    if useWheels:
        # Parses raw controller values
        if abs(x) > 0.1 or abs(y) > 0.1:
            # Acquires the sign of x and y
            ySine = abs(y)/y if y != 0 else 1
            xSine = abs(x)/x if x != 0 else 1

            if abs(x) <= 0.25:
                leftSpeed = y * 127 + ySine * 128
                rightSpeed = leftSpeed
            else:
                # Makes the forward turning joystick events have a little more leeway before going to the backward turning
                if ySine < 0 and y > -0.15:
                    ySine = +1

                # Makes only one of the sides move for the turns, starting at 128
                if x > 0:
                    leftSpeed = ySine * (x * 127 + xSine * 128)
                else:
                    rightSpeed = -ySine * (x * 127 + xSine * 128)

    parseAndSendMotorCode(leftSpeed, rightSpeed, beltSpeed, isBeltForward, actSpeed, isActForward, serial)

def parseAndSendMotorCode(leftSpeed: int, rightSpeed: int, beltSpeed: int, isBeltForward: bool, actSpeed: int, isActForward: bool, serial):
    # Parses speeds to have some low tolerance, because they will hardly ever actually be 0
    leftSpeed = round(leftSpeed) if abs(leftSpeed) > 30 else 0
    rightSpeed = round(rightSpeed) if abs(rightSpeed) > 30 else 0
    beltSpeed = round(beltSpeed) if abs(beltSpeed) > 30 else 0
    actSpeed = round(actSpeed) if abs(actSpeed) > 30 else 0
    
    # Parses direction of speeds into motor codes
    belt_motor_code = MotorCode.BELT_FORWARD if isBeltForward else MotorCode.BELT_BACKWARD
    act_motor_code = MotorCode.ACT_FORWARD if isActForward else MotorCode.ACT_BACKWARD
    left_motor_code = MotorCode.WHEELS_FORWARD if leftSpeed >= 0 else MotorCode.WHEELS_BACKWARD
    right_motor_code = MotorCode.WHEELS_FORWARD if rightSpeed >= 0 else MotorCode.WHEELS_BACKWARD
    serial.write_motor_command(left_motor_code, right_motor_code, belt_motor_code, act_motor_code, abs(leftSpeed), abs(rightSpeed), beltSpeed, actSpeed)


if __name__ == '__main__':
    app.run
    app.run(host="0.0.0.0", port=5000)