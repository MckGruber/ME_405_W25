import utime

class ClosedLoop:
  def __init__(self, set_point: float | int, p: float, i: float, d: float) -> None:
    self.set_point: float = float(set_point)
    self.p = p
    self.i = i
    self.d = d
    self.previous_error = 0
    self.integral = 0
    self.last_update_time = utime.ticks_ms()

  def update(self, measured_value: float) -> float:
    now = utime.ticks_ms()
    dt = utime.ticks_diff(self.last_update_time, now)
    
    error = self.set_point - measured_value

    P_out = self.p * error

    self.integral += error * dt 
    I_out = self.i * self.integral
    
    derivate = (error - self.previous_error) / dt
    D_out = self.d * derivate
    
    
    self.previous_error = error
    self.last_update_time = now


    return P_out + I_out + D_out
