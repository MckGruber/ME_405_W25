from prelude import *
from HAL import HAL
from math import pi
import time
#TODO Update encoder to have a hardware time update callback

def to_radians(ticks: int) -> float:
  return (ticks/120) * 2 * pi

class Encoder:
  def __init__(self, side: int, dt: int | float):
    self._side: int             = side 
    self.__hal__                = HAL.ENCODER.LEFT if self._side == Vehicle_Side.LEFT else HAL.ENCODER.RIGHT
    self.__position__: float    = 0
    self.prev_count: int        = 0
    self.delta: float           = 0
    self.dt                     = dt
    self.__check_value__        = (self.__hal__.TIM.period() + 1) / 2
    self.__velocity__           = 0

  
  def update(self) -> None:
    next_count = self.__hal__.TIM.counter()
    if self.prev_count - next_count > self.__check_value__:
      next_count += self.__hal__.TIM.period()
    elif next_count - self.prev_count > self.__check_value__:
      next_count -= self.__hal__.TIM.period()
    self.delta = next_count - self.prev_count
    self.prev_count = next_count
    self.__position__ += self.delta
    self.__velocity__ = to_radians(int(self.delta)) / (self.dt * 1e-3)

  def position(self, pos = None) -> float:
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
    return self.__velocity__