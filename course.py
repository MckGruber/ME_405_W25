from prelude import *
import HAL, motor_control_task
from task_share import Share
import gc


class CourseCompletion:
    S5_DISTANCE_SET_POINT = 100
    S10_HEADING_SET_POINT = 45 * 16
    S10_DISTANCE_SET_POINT = 100
    S20_HEADING_SET_POINT = -90 * 16
    S20_DISTANCE_SET_POINT = 0
    S30_HEADING_SET_POINT = None
    S30_DISTANCE_SET_POINT = None
    S40_DISTANCE_SET_POINT = None
    S50_HEADING_SET_POINT = None
    S50_DISTANCE_SET_POINT = None
    S55_HEADING_SET_POINT = None
    S55_DISTANCE_SET_POINT = None
    S60_HEADING_SET_POINT = None
    S60_DISTANCE_SET_POINT = None
    S70_HEADING_SET_POINT = None
    S70_DISTANCE_SET_POINT = None

    def __init__(self, debug=False) -> None:
        self.debug = debug
        self.button_function = self.default_button
        self.distance_set_point: None | int = None
        self.control_flag_share: None | Share = None
        self.motor_control_state_share: None | Share = None
        self.target_heading_share: None | Share = None
        self.left_motor_position_share: None | Share = None
        self.right_motor_position_share: None | Share = None
        self.heading_share: None | Share = None
        self.centroid_share: None | Share = None
        self.left_motor_position_reset_flag: None | Share = None
        self.right_motor_position_reset_flag: None | Share = None
        self.startng_heading_share: None | Share = None
        self.bump_sensor: None | Share = None

    def default_button(self):
        raise BaseException("Button Hit")

    def get_around_wall(self):
        raise BaseException("Not Implimented Yet")

    def wait(self):
        if (
            self.left_motor_position_share != None
            and self.control_flag_share != None
            and self.motor_control_state_share != None
            and self.target_heading_share != None
            and self.left_motor_position_share != None
            and self.right_motor_position_share != None
            and self.heading_share != None
            and self.centroid_share != None
            and self.left_motor_position_reset_flag != None
            and self.right_motor_position_reset_flag != None
            and self.startng_heading_share != None
            and self.bump_sensor != None
        ):
            while (
                self.left_motor_position_share.get()
                + self.right_motor_position_share.get()
            ) / 2 < self.distance_set_point:
                if self.debug:
                    print(
                        " | ".join(
                            [
                                f"State: {self.state}",
                                f"Target Heading: {self.target_heading_share.get()}",
                                f"Heading: {self.heading_share.get()}",
                                f"Distance: {(self.left_motor_position_share.get() + self.right_motor_position_share.get()) / 2}",
                                f"Target Distance: {self.distance_set_point}",
                            ]
                        )
                    )
                yield self.state
            self.left_motor_position_reset_flag.put(1)
            self.right_motor_position_reset_flag.put(1)

    def debug_print(self):
        if (
            self.left_motor_position_share != None
            and self.control_flag_share != None
            and self.motor_control_state_share != None
            and self.target_heading_share != None
            and self.left_motor_position_share != None
            and self.right_motor_position_share != None
            and self.heading_share != None
            and self.centroid_share != None
            and self.left_motor_position_reset_flag != None
            and self.right_motor_position_reset_flag != None
            and self.startng_heading_share != None
            and self.bump_sensor != None
        ):
            print(
                " | ".join(
                    [
                        f"State: {self.state}",
                        f"Target Heading: ({get_relative_angle(self.target_heading_share.get(), self.startng_heading_share.get()) / 16}, {self.target_heading_share.get()})",
                        f"Heading: ({get_relative_angle(self.heading_share.get(), self.startng_heading_share.get()) / 16}, {self.heading_share.get()})",
                        f"Distance: {(self.left_motor_position_share.get() + self.right_motor_position_share.get()) / 2}",
                        f"Target Distance: {self.distance_set_point}",
                    ]
                )
            )
        return

    def task(self, shares):

        (
            self.control_flag_share,
            self.motor_control_state_share,
            self.target_heading_share,
            self.left_motor_position_share,
            self.right_motor_position_share,
            self.heading_share,
            self.centroid_share,
            self.left_motor_position_reset_flag,
            self.right_motor_position_reset_flag,
            self.startng_heading_share,
            self.bump_sensor,
        ) = shares
        self.state = 0

        if (
            self.control_flag_share != None
            and self.motor_control_state_share != None
            and self.target_heading_share != None
            and self.left_motor_position_share != None
            and self.right_motor_position_share != None
            and self.heading_share != None
            and self.centroid_share != None
            and self.left_motor_position_reset_flag != None
            and self.right_motor_position_reset_flag != None
            and self.startng_heading_share != None
            and self.bump_sensor != None
        ):
            self.motor_control_state_share.put(
                motor_control_task.MotorControl.S1_LINE_PID_CALC
            )
            while True:
                if self.bump_sensor.get() == 1:
                    self.button_function()
                gc.collect()
                if self.control_flag_share.get() == 0:
                    if self.state != 0:
                        self.state = 0
                else:
                    ## self.state Map:
                    # S0: Starting ==>
                    # S5: Checkpoint 0 ==> Checkpoint 1
                    # S10: Checkpoint 1 ==> Checkpoint 2
                    # S20: Checkpoint 2 ==> Target 2
                    # S30: Target 2 ==> Checkpoint 3
                    # S40: Checkpoint 3 ==>
                    # S50: Grid ==>
                    # S55: Grid Middle Point ==>
                    # S57: To Wall ==>
                    # S60: Target 1 ==>
                    # S70: End ==>
                    # S80: Restart ↩

                    # """
                    # S0: Starting:
                    # while <all ir sensors are reading a value>:
                    #     <drive straight following starting heading>
                    # encoder_left.zero()
                    # encoder_right.zero()
                    # self.state = S5
                    # """
                    if self.state == 0:
                        print(f"Course State: {self.state }")
                        while self.centroid_share.get() == 0.0:
                            if self.debug:
                                " | ".join(
                                    [f"Centroid Error: {self.centroid_share.get()}"]
                                )
                            print(f"Course State: {self.state }")
                            yield self.state
                        self.motor_control_state_share.put(
                            motor_control_task.MotorControl.S0_STOP
                        )
                        print(f"Course State: {self.state }")
                        yield self.state
                        self.startng_heading_share.put(self.heading_share.get())
                        self.target_heading_share.put(self.heading_share.get())
                        self.left_motor_position_reset_flag.put(1)
                        self.right_motor_position_reset_flag.put(1)
                        self.startng_heading_share.put(self.startng_heading_share.get())
                        print(f"Starting Heading: {self.startng_heading_share.get()}")
                        self.state = 5
                    # '''
                    # S5: Checkpoint One:
                    #     while heading < starting_heading - 90°:
                    #         motor_control_state ==> Line Following
                    #     target_heading.put(starting_heading - 90°)
                    #     motor_control_state ==> Heading Following
                    #     while (<Left Motor Position> + <Right Motor Position>) / 2 < CHECKPOINT_ONE_DISTANCE_SET_POINT:
                    #         yeild
                    #     self.state = S10
                    # '''
                    elif self.state == 5:
                        print(f"Course State: {self.state}")
                        self.distance_set_point = CourseCompletion.S5_DISTANCE_SET_POINT
                        self.target_heading_share.put(self.startng_heading_share.get())
                        self.motor_control_state_share.put(
                            motor_control_task.MotorControl.S2_HEADING_PID_CALC
                        )
                        while (
                            self.left_motor_position_share.get()
                            + self.right_motor_position_share.get()
                        ) / 2 < self.distance_set_point:
                            if self.debug:
                                self.debug_print()
                            print(f"Course State: {self.state }")
                            yield self.state
                        self.left_motor_position_reset_flag.put(1)
                        self.right_motor_position_reset_flag.put(1)
                        self.state = 10
                    elif self.state == 10:
                        print(f"Course State: {self.state }")
                        self.target_heading_share.put(
                            get_relative_angle(
                                self.S10_HEADING_SET_POINT,
                                self.startng_heading_share.get(),
                            )
                        )
                        self.distance_set_point = (
                            CourseCompletion.S10_DISTANCE_SET_POINT
                        )
                        while (
                            self.left_motor_position_share.get()
                            + self.right_motor_position_share.get()
                        ) / 2 < self.distance_set_point:
                            if self.debug:
                                self.debug_print()
                            yield self.state
                        self.left_motor_position_reset_flag.put(1)
                        self.right_motor_position_reset_flag.put(1)
                        self.state = 20
                    elif self.state == 20:
                        print(f"Course State: {self.state}")
                        self.target_heading_share.put(
                            get_relative_angle(
                                self.S20_HEADING_SET_POINT,
                                self.startng_heading_share.get(),
                            )
                        )
                        self.distance_set_point = (
                            CourseCompletion.S20_DISTANCE_SET_POINT
                        )
                        while (
                            self.left_motor_position_share.get()
                            + self.right_motor_position_share.get()
                        ) / 2 < self.distance_set_point:
                            if self.debug:
                                self.debug_print()
                            yield self.state
                        self.left_motor_position_reset_flag.put(1)
                        self.right_motor_position_reset_flag.put(1)
                        self.state = 30
                    if self.state > 20:
                        return
                yield self.state
