from prelude import *
from task_share import Share
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
    def __init__(
        self,
        encoder_dt: int,
        line_pid_controler: ClosedLoop,
        heading_pid_controler: ClosedLoop,
    ) -> None:
        self.line_controler = line_pid_controler
        self.heading_controler = heading_pid_controler
        self.controler: ClosedLoop | None
        self.state = 0  # Initial FSM state
        self.motor_left = Motor(Vehicle_Side.LEFT)
        self.motor_right = Motor(Vehicle_Side.RIGHT)
        self.was_off = True

    def pid(self, error: float) -> None:
        if self.controler != None:
            self.new_set_point = self.controler.update(error)
            # print(f'error: {error}', end=" | ")
            # print(f'new set point: {"Left" if  abs(self.new_set_point) > 0 else "Right"} -> {MOTOR_SET_POINT + abs(self.new_set_point)}')
            if abs(error) > 0.1:
                self.motor_left.__effort__(MOTOR_SET_POINT + self.new_set_point / 2)
                self.motor_right.__effort__(MOTOR_SET_POINT - self.new_set_point / 2)

    @classmethod
    def task(cls, shares: tuple):
        # TODO Update this pid with the new numbers - We need to redo Lab 2 but correctly so we can actually get the numbers we need to calculate the speed
        line_pid_controler = ClosedLoop(kp=5, ki=0.5, kd=0)
        heading_pid_controler = ClosedLoop(kp=2, ki=0.01, kd=0.002)
        motor_control = cls(
            20,
            line_pid_controler=line_pid_controler,
            heading_pid_controler=heading_pid_controler,
        )
        # Get shared variables
        centroid_share: Share
        heading_share: Share
        pitch_share: Share
        roll_share: Share
        gyro_x_share: Share
        gyro_y_share: Share
        gyro_z_share: Share
        control_flag: Share
        target_heading: Share
        left_motor_pwm_effort_share: Share
        right_motor_pwm_effort_share: Share
        (
            centroid_share,
            heading_share,
            pitch_share,
            roll_share,
            gyro_x_share,
            gyro_y_share,
            gyro_z_share,
            control_flag,
            target_heading,
            # left_motor_pwm_effort_share,
            # right_motor_pwm_effort_share,
        ) = shares
        # print('shares parsed successfully')
        motor_control.motor_left.set_speed(MOTOR_SET_POINT)
        motor_control.motor_right.set_speed(MOTOR_SET_POINT)
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
                        error1: int = (
                            target_heading.get() - heading_share.get()
                        ) % 5670
                        error2: int = error1 - 5670 if error1 > 0 else error1 + 5670
                        error = (
                            error1 / 16
                            if min(abs(error1), abs(error2)) == abs(error1)
                            else error2 / 16
                        )
                        motor_control.pid(error)
                        print(
                            f"Error: ({error1/16}, {error2/16}) | Target: {target_heading.get()} | Heading: {heading_share.get()} | Left Motor: {motor_control.motor_left.__effort__() * (-1 if motor_control.motor_left.direction != 0 else 1)} | Right Motor: {motor_control.motor_right.__effort__() * (-1 if motor_control.motor_right.direction != 0 else 1)}",
                            end=" | ",
                        )
                    else:
                        pass
                    motor_control.state = (
                        S1_LINE_PID_CALC
                        if target_heading.get() == None
                        else S2_HEADING_PID_CALC
                    )
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
                motor_control.state = (
                    S1_LINE_PID_CALC
                    if target_heading.get() == None
                    else S2_HEADING_PID_CALC
                )
            else:
                continue

            yield motor_control.state  # Yield control to the scheduler
