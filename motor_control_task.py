from prelude import *
import cotask, task_share
from closed_loop import ClosedLoop
from motor import Motor
from prelude import Vehicle_Side
from encoder import Encoder
import HAL

S1_PID_CALC = 1
S0_STOP = -1

class MotorControl:
    # FSM states
    def __init__(self, encoder_dt: int, pid_controler: ClosedLoop) -> None:
        self.controler = pid_controler
        self.state = 0  # Initial FSM state
        self.motor_left = Motor(Vehicle_Side.LEFT)
        self.motor_right = Motor(Vehicle_Side.RIGHT)
        self.encoder = {
            "Left": Encoder(Vehicle_Side.LEFT, encoder_dt),
            "Right": Encoder(Vehicle_Side.RIGHT, encoder_dt)
        }
        for encoder in self.encoder.values():
            encoder.zero()  # Reset encoder readings to zero

        self.was_off = True
    def pid(self, centroid: float | None) -> None:
        if centroid != None:
            self.new_set_point = self.controler.update(measured_value= centroid) / 10
            print(f'Centroid: {centroid}')
            self.update()
    
    def update(self):
        if self.new_set_point == 0:
            return
        # if self.motor_left.effort() >= 25:
        #     raise BaseException("Too much motor")
        elif self.new_set_point > 0:
            new_effort = (self.motor_left.effort() + self.new_set_point)
        else:
            new_effort = (self.motor_left.effort() + self.new_set_point)
        # print(f'Effort: {self.motor_left.effort()*(self.motor_left.direction*-1 if self.motor_left.direction == 1 else 1)} -> {new_effort}')
        self.motor_left.effort(new_effort)


    @classmethod
    def task(cls, shares):
        pid_controler = ClosedLoop(0.0, kp=-2.4, ki=-.18, kd=.5)
        motor_control = cls(20, pid_controler)
        # Get shared variables
        centroid_share: task_share.Share = shares[0]  # Get line sensor centroid data
        control_flag:task_share.Share = shares[1]  # Get shared control flag (button press)
        motor_control.motor_left.effort(15)
        motor_control.motor_right.effort(15)
        while True:
            if control_flag.get() == 1 and motor_control.state != S0_STOP:
                # print(f"Motor Conrol: {motor_control.state}")
                
                # Read the centroid value from the line sensor
                centroid: float | None = centroid_share.get()
                if centroid is not None:
                    # print(f"Centroid: {centroid}")

                    # TODO: Implement closed-loop motor control logic here
                    if motor_control.state == S1_PID_CALC:
                        motor_control.pid(centroid)
                    else:
                        motor_control.state = S1_PID_CALC
                else:
                    pass
                yield motor_control.state

            elif control_flag.get() == 0 and motor_control.state != S0_STOP:
                print("Closed-loop control OFF")
                
                # Stop the motors when control is disabled
                motor_control.motor_left.disable()
                motor_control.motor_right.disable()
                motor_control.state = S0_STOP
            elif control_flag.get() == 1 and motor_control.state == S0_STOP:
                print("Closed-loop control ON")
                motor_control.motor_left.enable()
                motor_control.motor_right.enable()
                motor_control.state = S1_PID_CALC
            else:
                continue

            yield motor_control.state  # Yield control to the scheduler
