class Vehicle_Side:
    LEFT = 0
    RIGHT = 1


class MotorDirection:
    FWD = 0
    REV = 1


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


OM_SET = 0
V_LIN_SET = 5

MOTOR_SET_POINT = 0

MAX_SPEED = 300

import task_share


def echo(buffer: task_share.Queue, string: str, end="\n"):
    for char in string + end:
        buffer.put(ord(char))
