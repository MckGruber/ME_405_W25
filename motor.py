from prelude import *
import HAL
from closed_loop import ClosedLoop
import task_share
from encoder import Encoder


class Motor:
    def __init__(self, side: int) -> None:
        self._side: int = side
        self.__hal__ = (
            HAL.__MOTOR_LEFT__ if side == Vehicle_Side.LEFT else HAL.__MOTOR_RIGHT__
        )
        self.direction = (
            MotorDirection.FWD
            if self.__hal__.DIRECTION.value() == MotorDirection.FWD
            else MotorDirection.REV
        )
        self.is_on = bool(self.__hal__.ENABLE.value())
        self.controller: ClosedLoop = ClosedLoop(kp=2, ki=0.01, kd=0.005)
        self.velocity_set_point_share: task_share.Share | None = None
        self.encoder = Encoder(side)

    def __set_dir__(self, dir: int):
        self.direction = dir
        self.__hal__.DIRECTION.value(dir)

    def __effort__(self, value: int | float | None = None) -> int | float:
        if value == None:
            self.__hal__.PWM.pulse_width_percent()
            return self.__hal__.PWM.pulse_width_percent()

        effort = (
            clamp(abs(value), -100, 100)
            if type(value) == int
            else float(clamp(abs(value), -100, 100))
        )
        self.__set_dir__(MotorDirection.FWD if value > 0 else MotorDirection.REV)
        self.__hal__.PWM.pulse_width_percent(effort)

        return effort

    def set_speed(self, speed: int) -> None:
        # Ensure speed is within valid range
        speed = clamp(
            speed, -MAX_SPEED, MAX_SPEED
        )  # Ensure speed stays within valid range
        if self.velocity_set_point_share != None:
            # TODO set the pwm set point to what this effort is 'supposed' to be
            self.velocity_set_point_share.put(speed)

    def enable(self):
        if self.is_on:
            return
        self.is_on = True
        self.__hal__.ENABLE.high()
        return

    def disable(self):
        if not self.is_on:
            return
        self.is_on = False
        self.__hal__.ENABLE.low()

    def task(self, shares):
        self.velocity_set_point_share: task_share.Share | None = shares[0]
        while True:
            if self.velocity_set_point_share != None:
                error = self.velocity_set_point_share.get() - self.encoder.velocity()
            self.__effort__(self.__effort__() + self.controller.update(error))
            yield
