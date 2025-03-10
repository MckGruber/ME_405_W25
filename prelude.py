class Vehicle_Side:
    LEFT = 0
    RIGHT = 1


class MotorDirection:
    FWD = 0
    REV = 1


def get_voltage() -> float:
    import HAL

    voltage = HAL._ADC_A5.read() * (3.3 / 4095) * (14.7 / 4.7)
    # if voltage < 5.5:
    # raise BaseException(f"Voltage Too Low, Change Batteries. Voltage: {voltage}")
    # print(f"Voltage Too Low, Change Batteries. Voltage: {voltage}")
    return voltage


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


# Motor Set Points
SPEED_SET_POINT = 50
MOTOR_SET_POINT_PERCENT = clamp((SPEED_SET_POINT * (7.2 / 3.11)), 0, 100) / 100

# Course Set Points
STDEV_SET_POINT = None
S5_DISTANCE_SET_POINT = None
S10_DISTANCE_SET_POINT = None
S20_HEADING_SET_POINT = None
S20_DISTANCE_SET_POINT = None
S30_HEADING_SET_POINT = None
S30_DISTANCE_SET_POINT = None
S40_DISTANCE_SET_POINT = None
S50_HEADING_SET_POINT = None
S50_DISTANCE_SET_POINT = None
S55_HEADING_SET_POINT = None
S55_DISTANCE_SET_POINT = None
S60_HEADING_SET_POINT = None
S60_DISTANCE_SET_POINT = None
S70_HEADING_SET_POINT = None
S70_DISTANCE_SET_POINT = None

DEBUG = False
