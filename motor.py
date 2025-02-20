from prelude import *
import HAL

class Motor:
  def __init__(self, side: int) -> None:
    self._side: int = side
    self.__hal__ = HAL.__MOTOR_LEFT__ if side == Vehicle_Side.LEFT else HAL.__MOTOR_RIGHT__
    self.direction = MotorDirection.FWD if self.__hal__.DIRECTION.value() == MotorDirection.FWD else MotorDirection.REV
    self.is_on = bool(self.__hal__.ENABLE.value())
    pass

  def set_dir(self, dir: int):
    self.__hal__.DIRECTION.value(dir)

  def effort(self, value: int | float | None = None) -> int | float:
    if value == None:
      self.__hal__.PWM.pulse_width_percent()
      return self.__hal__.PWM.pulse_width_percent()
    
    effort = clamp(abs(value), -100, 100) if type(value) == int else float(clamp(abs(value), -100, 100))
    self.set_dir(MotorDirection.FWD if value > 0 else MotorDirection.REV)
    self.__hal__.PWM.pulse_width_percent(effort)
    return effort
    
  def effort_raw(self, value: int | None = None) -> int:
    if value == None:
      self.__hal__.PWM.pulse_width()
      return self.__hal__.PWM.pulse_width()
    else:
      effort = clamp(abs(value), -100, 100)
      self.set_dir(MotorDirection.FWD if value > 0 else MotorDirection.REV)
      self.__hal__.PWM.pulse_width(effort)
      return effort
    
  def set_speed(self, speed: int) -> None:
    # Ensure speed is within valid range
    speed = clamp(speed, -100, 100)  # Ensure speed stays within valid range

    if speed == 0:
        self.__hal__.PWM.pulse_width_percent(0)  # Stop the motor
    else:
        direction = MotorDirection.FWD if speed > 0 else MotorDirection.REV
        self.set_dir(direction)  # Set correct motor direction
        self.__hal__.PWM.pulse_width_percent(abs(speed))  # Apply speed as PWM duty cycle

  
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