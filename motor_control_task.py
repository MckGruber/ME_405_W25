from prelude import *
import cotask, task_share
from closed_loop import ClosedLoop
from motor import Motor
from prelude import Vehicle_Side
from encoder import Encoder
import HAL

S1_LINE_PID_CALC = 1
S2_HEADING_PID_CALC = 2
S0_STOP = -1

class MotorControl:
    # FSM states
    def __init__(self, encoder_dt: int, line_pid_controler: ClosedLoop, heading_pid_controler: ClosedLoop) -> None:
        self.line_controler = line_pid_controler
        self.heading_controler = heading_pid_controler
        self.controler: ClosedLoop | None
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
    def pid(self, error: float) -> None:
        if self.controler != None:
            self.new_set_point = self.controler.update(error)
            # print(f'error: {error}', end=" | ")
            # print(f'new set point: {"Left" if  abs(self.new_set_point) > 0 else "Right"} -> {MOTOR_SET_POINT + abs(self.new_set_point)}')
            if abs(error) > .1:
                self.update()
            else:
                self.motor_left.effort(MOTOR_SET_POINT)
                self.motor_right.effort(MOTOR_SET_POINT)
    
    def update(self):
        self.motor_left.effort(MOTOR_SET_POINT + self.new_set_point / 2)
        self.motor_right.effort(MOTOR_SET_POINT - self.new_set_point / 2)


    @classmethod
    def task(cls, shares):
        line_pid_controler = ClosedLoop(kp=5, ki=.5, kd=0)
        heading_pid_controler = ClosedLoop (kp = 2, ki=0.01, kd=0.002)
        motor_control = cls(20, line_pid_controler = line_pid_controler, heading_pid_controler = heading_pid_controler)
        # Get shared variables
        centroid_share: task_share.Share    = shares[0]
        heading_share: task_share.Share     = shares[1]
        pitch_share: task_share.Share       = shares[2]
        roll_share: task_share.Share        = shares[3]
        gyro_x_share: task_share.Share      = shares[4]
        gyro_y_share: task_share.Share      = shares[5]
        gyro_z_share: task_share.Share      = shares[6]
        control_flag: task_share.Share      = shares[7]
        target_heading: task_share.Share    = shares[8]
        # print('shares parsed successfully')
        motor_control.motor_left.effort(MOTOR_SET_POINT)
        motor_control.motor_right.effort(MOTOR_SET_POINT)
        while True:
            if control_flag.get() == 1 and motor_control.state != S0_STOP:
                # print(f"Motor Conrol: {motor_control.state}")
                
                # Read the centroid value from the line sensor
                centroid: float | None = centroid_share.get()
                
                if centroid != None and target_heading.get() != None:
                    # print(f"Centroid: {centroid}")

                    # TODO: Implement closed-loop motor control logic here
                    if motor_control.state == S1_LINE_PID_CALC:
                        motor_control.controler = motor_control.line_controler
                        motor_control.pid(0 - centroid)
                    elif motor_control.state == S2_HEADING_PID_CALC:
                        # print(f"Heading: {heading_share.get()} | Target Heading: {target_heading.get()}")
                        motor_control.controler = motor_control.heading_controler
                        error1: int = (target_heading.get() - heading_share.get()) % 5670
                        error2: int = error1 - 5670 if error1 > 0 else error1 + 5670
                        error = error1/16 if min(abs(error1), abs(error2)) == abs(error1) else error2/16
                        motor_control.pid(error)
                        print(f'Error: ({error1/16}, {error2/16}) | Target: {target_heading.get()} | Heading: {heading_share.get()} | Left Motor: {motor_control.motor_left.effort() * (-1 if motor_control.motor_left.direction != 0 else 1)} | Right Motor: {motor_control.motor_right.effort() * (-1 if motor_control.motor_right.direction != 0 else 1)}', end=" | ")
                    else:
                        pass
                    motor_control.state = S1_LINE_PID_CALC if target_heading.get() == None else S2_HEADING_PID_CALC
                else:
                    print("NO CENTROID FOUND")
                    # motor_control.motor_left.effort(15)
                    # motor_control.motor_right.effort(15)
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
                motor_control.state = S1_LINE_PID_CALC if target_heading.get() == None else S2_HEADING_PID_CALC
            else:
                continue

            yield motor_control.state  # Yield control to the scheduler
