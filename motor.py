from prelude import *
import HAL

class Motor:
  def __init__(self, side: int) -> None:
    self._side: int = side
    self.__hal__ = HAL.__MOTOR_LEFT__ if self._side == Vehicle_Side.LEFT else HAL.__MOTOR_RIGHT__
    self.direction = MotorDirection.FWD if self.__hal__.DIRECTION.value() == MotorDirection.FWD else MotorDirection.REV
    self.is_on = bool(self.__hal__.ENABLE.value())
    pass

  def set_dir(self, dir: int):
    self.__hal__.DIRECTION.value(dir)

  def effort(self, value: int | None) -> int | None:
    if value == None:
      self.__hal__.PWM.pulse_width_percent()
      return self.__hal__.PWM.pulse_width_percent()
    else:
      effort = clamp(abs(value), -100, 100)
      self.set_dir(MotorDirection.FWD if value > 0 else MotorDirection.REV)
      self.__hal__.PWM.pulse_width_percent(effort)
    return

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