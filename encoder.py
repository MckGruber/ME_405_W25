from prelude import *
from HAL import HAL
from math import pi
import utime

# TODO Update encoder to have a hardware time update callback


def to_radians(ticks: int) -> float:
    return (ticks / 120) * 2 * pi


class Encoder:
    def __init__(self, side: int):
        self._side: int = side
        self.__hal__ = (
            HAL.ENCODER.LEFT if self._side == Vehicle_Side.LEFT else HAL.ENCODER.RIGHT
        )
        self.__position__: float = 0
        self.prev_count: int = 0
        self.delta: float = 0
        self.last_update_time = utime.ticks_ms()
        self.__check_value__ = (self.__hal__.TIM.period() + 1) / 2
        self.__velocity__ = 0

    def update(self) -> None:
        next_count = self.__hal__.TIM.counter()
        if self.prev_count - next_count > self.__check_value__:
            next_count += self.__hal__.TIM.period()
        elif next_count - self.prev_count > self.__check_value__:
            next_count -= self.__hal__.TIM.period()
        self.delta = next_count - self.prev_count
        self.prev_count = next_count
        self.__position__ += self.delta
        now = utime.ticks_ms()
        self.__velocity__ = to_radians(int(self.delta)) / (
            utime.ticks_diff(now, self.last_update_time) * 1e-3
        )
        self.last_update_time = now

    def position(self, pos=None) -> float:
        if pos == None:
            return to_radians(int(self.__position__))
        else:
            self.__position__ = pos
            return pos

    def zero(self):
        self.__position__ = 0
        self.prev_count = 0
        self.__hal__.TIM.counter(0)

    def velocity(self) -> float:
        self.update()
        return self.__velocity__
