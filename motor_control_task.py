from prelude import *
import cotask, task_share
from closed_loop import ClosedLoop
from motor import Motor
from prelude import Vehicle_Side
from encoder import Encoder

S1_PID_CALC = 0
S2_MOTOR_UPDATE = 1
S0_STOP = -1

class MotorControl:
    # FSM states
    def __init__(self, encoder_dt: int, pid_controler: ClosedLoop) -> None:
        self.controler = pid_controler
        self.state = 0  # Initial FSM state
        self.motor = {
            "Left": Motor(Vehicle_Side.LEFT),
            "Right": Motor(Vehicle_Side.RIGHT)
        }
        self.encoder = {
            "Left": Encoder(Vehicle_Side.LEFT, encoder_dt),
            "Right": Encoder(Vehicle_Side.RIGHT, encoder_dt)
        }
        for encoder in self.encoder.values():
            encoder.zero()  # Reset encoder readings to zero
    def pid(self, centroid: float | None) -> None:
        if centroid != None:
            self.new_set_point = self.controler.update(measured_value= centroid)
    
    def update(self):
        if self.new_set_point == 0:
            return
        elif self.new_set_point > 0:
            self.motor["Left"].effort(self.motor["Left"].effort() + round(abs(clamp(self.new_set_point, 0, 100)))) # type: ignore
        else:
            self.motor["Right"].effort(self.motor["Left"].effort() + round(abs(clamp(self.new_set_point, 0, 100))))


    @classmethod
    def task(cls, shares):
        pid_controler = ClosedLoop(0.0, p=1.0, i=0.1, d=0.05)
        motor_control = cls(20, pid_controler)
        # Get shared variables
        centroid_share = shares[0]  # Get line sensor centroid data
        control_flag = shares[1]  # Get shared control flag (button press)

        while True:
            if control_flag.get() == 1 and motor_control.state != S0_STOP:
                print("Closed-loop control ON")
                
                # Read the centroid value from the line sensor
                centroid = centroid_share.get()
                if centroid is not None:
                    print(f"Centroid: {centroid}")

                    # TODO: Implement closed-loop motor control logic here
                    if motor_control.state == S1_PID_CALC:
                        motor_control.pid(centroid)
                        motor_control.state = S2_MOTOR_UPDATE
                    elif motor_control.state == S2_MOTOR_UPDATE:
                            motor_control.update()
                            motor_control.state = S1_PID_CALC
                    else:
                            motor_control.state = S1_PID_CALC
                else:
                    print("No line detected.")

            else:
                print("Closed-loop control OFF")
                
                # Stop the motors when control is disabled
                for motor in motor_control.motor.values():
                    motor.set_speed(0)

            yield motor_control.state  # Yield control to the scheduler
