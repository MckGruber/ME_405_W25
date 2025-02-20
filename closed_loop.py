import utime

class ClosedLoop:
  def __init__(self, set_point: float | int, kp: float, ki: float, kd: float) -> None:
    self.set_point: float = float(set_point)
    self.kp = kp
    self.ki = ki
    self.kd = kd
    self.previous_error = 0
    self.integral = 0
    self.last_update_time = utime.ticks_ms()

  def update(self, measured_value: float | None) -> float:
    measured_value = measured_value if measured_value != None else 0.0
    now = utime.ticks_ms()
    dt = utime.ticks_diff(self.last_update_time, now) / 1000
    
    error = self.set_point - measured_value

    P_out = self.kp * error

    self.integral += error * dt 
    I_out = self.ki * self.integral
    
    derivate = (error - self.previous_error) / dt
    D_out = self.kd * derivate
    
    
    self.previous_error = error
    self.last_update_time = now

    print(f'kp: {P_out} | ki: {I_out} | kd: {D_out}')
    return P_out + I_out + D_out
