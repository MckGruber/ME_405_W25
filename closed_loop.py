import utime


class ClosedLoop:
    def __init__(self, kp: float, ki: float, kd: float) -> None:
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.previous_error = 0
        self.integral = 0
        self.last_update_time = utime.ticks_ms()
        self.last_error = 0
        self.min_offset = 1.0

    def update(self, error: float) -> float:

        now = utime.ticks_ms()
        dt = utime.ticks_diff(self.last_update_time, now) / 1000

        P_out = self.kp * error

        self.integral += error * dt
        I_out = self.ki * self.integral

        derivate = (error - self.previous_error) / dt
        D_out = self.kd * derivate

        self.previous_error = error
        self.last_update_time = now
        pid = P_out + I_out + D_out

        print(f"kp: {P_out} | ki: {I_out} | kd: {D_out}")
        return P_out + I_out + D_out
