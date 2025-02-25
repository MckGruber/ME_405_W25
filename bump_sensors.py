import HAL

class BumpSensor:
    #  BumpSensor class to manage bump sensors
    def __init__(self):
        # Initialize bump sensors
        self.left_sensors = [
            HAL.__BUMP_SENSOR__.LEFT.INSIDE,
            HAL.__BUMP_SENSOR__.LEFT.MIDDLE,
            HAL.__BUMP_SENSOR__.LEFT.OUTSIDE
        ]
        self.right_sensors = [
            HAL.__BUMP_SENSOR__.RIGHT.INSIDE,
            HAL.__BUMP_SENSOR__.RIGHT.MIDDLE,
            HAL.__BUMP_SENSOR__.RIGHT.OUTSIDE
        ]

    def read_left(self):
        # Reads the state of the left bump sensors.
        return [not sensor.value() for sensor in self.left_sensors]

    def read_right(self):
        # Reads the state of the right bump sensors.
        return [not sensor.value() for sensor in self.right_sensors]

    def any_pressed(self):
        # Checks if any of the bump sensors are pressed.
        return any(self.read_left()) or any(self.read_right())

    def get_collision_side(self):
        # Determines which side of the robot has a collision.
        left_hit = any(self.read_left())
        right_hit = any(self.read_right())

        # Determine the collision side for debugging purposes.
        if left_hit and right_hit:
            return "BOTH"
        elif left_hit:
            return "LEFT"
        elif right_hit:
            return "RIGHT"
        else:
            return "NONE"
