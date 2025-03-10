from prelude import *
from task_share import Share
from closed_loop import ClosedLoop
import HAL


class MotorControl:
    S1_LINE_PID_CALC = 1
    S2_HEADING_PID_CALC = 2
    S0_STOP = -1

    # FSM states
    def __init__(
        self,
        yaw_effort_percent_share: Share,
    ) -> None:
        self.yaw_effort_percent_share = yaw_effort_percent_share
        self.controler: ClosedLoop | None
        self.state = MotorControl.S0_STOP  # Initial FSM state

    def pid(
        self,
        error: float,
    ) -> None:
        if self.controler != None:
            self.new_set_point = self.controler.update(error)
            self.yaw_effort_percent_share.put(self.new_set_point)
            # self.left_motor_velocity_set_point_share.put(self.new_set_point / 2)
            # self.right_motor_velocity_set_point_share.put(-self.new_set_point / 2)

    @classmethod
    def task(cls, shares: tuple):
        # TODO Retune these after the cascade control rewrite
        line_pid_controler = ClosedLoop(
            # Almost Working, (20, .2, .02)
            kp=(50 * MOTOR_SET_POINT_PERCENT),
            ki=0.2,
            kd=0.002,
        )
        heading_pid_controler = ClosedLoop(
            # Old Values before Cascade Control: (2, 0.01, 0.002)
            # Values were the old values, but halved, in accordance to the change to the self.pid() function
            kp=1,
            ki=0.005,
            kd=0.001,
        )

        # Get shared variables
        centroid_share: Share
        heading_share: Share
        target_heading_share: Share
        motor_control_state_share: Share
        control_flag: Share
        yaw_effort_percent_share: Share
        (
            centroid_share,
            heading_share,
            target_heading_share,
            motor_control_state_share,
            control_flag,
            yaw_effort_percent_share,
        ) = shares
        motor_control = cls(
            yaw_effort_percent_share,
        )
        while True:
            if control_flag.get() == 0:
                if motor_control.state != motor_control.S0_STOP:
                    motor_control.state = motor_control.S0_STOP
            else:
                ## -------------------------------------- Main Course Completion Loop ----------------------------------------------- ##
                # each state should do the following steps:
                # 1. set the appropriate ClosedLoop Controler
                # 2. Defines a set point
                # 3. Defines an error function
                # 4. calculates the error
                # 5. passes the error to the motor_control.pid() function

                # -------------------------------------------Unpacking Share values-------------------------------------------------------- #
                centroid_error: float = centroid_share.get()
                target_heading: float = target_heading_share.get()
                motor_control.state = motor_control_state_share.get()
                # -------------------------------------------\Unpacking Share values-------------------------------------------------------- #

                # --------------- S1: Follow the Line Sensor (Default) ----------------- #
                if motor_control.state == MotorControl.S1_LINE_PID_CALC:
                    motor_control.controler = line_pid_controler
                    motor_control.pid(centroid_error)
                    if DEBUG:
                        print(
                            " | ".join(
                                [
                                    f"Error: ({centroid_error})",
                                    f"Left Motor: {HAL.__MOTOR_LEFT__.PWM.pulse_width_percent() * (-1 if HAL.__MOTOR_LEFT__.DIRECTION.value() != MotorDirection.FWD else 1)}",
                                    f"Right Motor: {HAL.__MOTOR_RIGHT__.PWM.pulse_width_percent() * (-1 if HAL.__MOTOR_RIGHT__.DIRECTION.value() != MotorDirection.FWD else 1)}",
                                ]
                            )
                        )
                # --------------- \S1: Follow the Line Sensor (Default) ----------------- #

                # ------------------------- S2: Follow A Heading ------------------------- #
                if motor_control.state == MotorControl.S2_HEADING_PID_CALC:
                    motor_control.controler = heading_pid_controler
                    error1: int = (target_heading - heading_share.get()) % 5670
                    error2: int = error1 - 5670 if error1 > 0 else error1 + 5670
                    error = (
                        error1 / 16
                        if min(abs(error1), abs(error2)) == abs(error1)
                        else error2 / 16
                    )
                    motor_control.pid(error)
                    if DEBUG:
                        print(
                            " | ".join(
                                [
                                    f"Error: ({error1/16}, {error2/16})",
                                    f"Target: {target_heading}",
                                    f"Heading: {heading_share.get()}",
                                    f"Left Motor: {HAL.__MOTOR_LEFT__.PWM.pulse_width_percent() * (-1 if HAL.__MOTOR_LEFT__.DIRECTION.value() != MotorDirection.FWD else 1)}",
                                    f"Right Motor: {HAL.__MOTOR_RIGHT__.PWM.pulse_width_percent() * (-1 if HAL.__MOTOR_RIGHT__.DIRECTION.value() != MotorDirection.FWD else 1)}",
                                ]
                            )
                        )
                # ------------------------- \S2: Follow A Heading ------------------------- #

                # Default Action: Yeild unimplimented State
            yield motor_control.state
