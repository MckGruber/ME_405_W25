from prelude import *


class Shares:
    def __init__(self):
        self.is_built = False

    def build(self):
        import task_share, userbutton

        self.is_built = True
        ## ----------------------- <Shares> -------------------------- ##

        # Create shared variable for centroid data
        self.centroid_share = task_share.Share("f", True, "Centroid")
        self.centroid_stdev_share = task_share.Share(
            "f", True, "Centroid Standard Deviation"
        )

        # Get shared control flag from userbutton.py
        self.control_flag = userbutton.get_control_flag_share()

        # Create an IMU Angle Share
        self.heading_share = task_share.Share("f", True, "Heading Angle")
        self.pitch_share = task_share.Share("f", True, "Pitch Angle")
        self.roll_share = task_share.Share("f", True, "Roll Angle")

        # Create an IMU Velocity Share
        self.gyro_x_share = task_share.Share("f", True, "X Angular Velocity")
        self.gyro_y_share = task_share.Share("f", True, "Y Angular Velocity")
        self.gyro_z_share = task_share.Share("f", True, "Z Angular Velocity")

        # Target Heading Share
        self.target_heading_share = task_share.Share("f", True, "Target Heading")

        # Motor Velocity Share
        # self.left_motor_velocity_set_point_share =task_share.Share(
        #     "f", True, "Left Motor Velocity"
        # )
        # self.right_motor_velocity_set_point_share =task_share.Share(
        #     "f", True, "Right Motor Velocity"
        # )
        self.yaw_velocity_share = task_share.Share("f", True, "Yaw Velocity Share")

        # Position Shares
        self.left_motor_position_share = task_share.Share(
            "f", True, "Left Motor Position"
        )
        self.right_motor_position_share = task_share.Share(
            "f", True, "Right Motor Position"
        )
        self.right_motor_position_reset_flag = task_share.Share(
            "H", True, "Right Motor Position Reset Flag"
        )
        self.left_motor_position_reset_flag = task_share.Share(
            "H", True, "Left Motor Position Reset Flag"
        )

        # Motor Control State Share
        self.motor_control_state_share = task_share.Share(
            "h", True, "Motor Control State"
        )

        ## ----------------------- </Shares> ----------------------- ##
        return self


class TaskBuilder:
    import cotask

    def __init__(self) -> None:
        import cotask

        self.task_list: list[cotask.Task] = []
        self.shares = Shares()
        self.is_built = False

    def vehicle_conrol(self):
        import cotask, motor_control_task

        if self.is_built:
            self.fail()
        if not self.shares.is_built:
            self.shares.build()
        motor_task = cotask.Task(
            motor_control_task.MotorControl.task,
            name="MotorControl",
            priority=20,
            period=10,
            profile=True,
            trace=True,
            shares=(
                self.shares.centroid_share,
                self.shares.heading_share,
                self.shares.target_heading_share,
                self.shares.motor_control_state_share,
                self.shares.control_flag,
                self.shares.yaw_velocity_share,
            ),
        )
        self.append(motor_task)
        return self

    def line_sensor(self):
        import cotask, line_sensor

        if self.is_built:
            self.fail()
        if not self.shares.is_built:
            self.shares.build()
        self.line_task = cotask.Task(
            line_sensor.LineSensor().task,
            name="LineSensor",
            priority=10,
            period=10,
            profile=True,
            trace=True,
            shares=(
                self.shares.control_flag,
                self.shares.centroid_share,
                self.shares.centroid_stdev_share,
            ),
        )
        self.append(self.line_task)
        return self

    def imu(self):
        import cotask, bno055

        if self.is_built:
            self.fail()
        if not self.shares.is_built:
            self.shares.build()
        self.imu_task = cotask.Task(
            bno055.BNO055().task,
            name="IMU",
            priority=10,
            period=10,
            profile=True,
            trace=True,
            shares=(
                self.shares.control_flag,
                self.shares.heading_share,
                self.shares.pitch_share,
                self.shares.roll_share,
                self.shares.gyro_x_share,
                self.shares.gyro_y_share,
                self.shares.gyro_z_share,
            ),
        )
        self.append(self.imu_task)
        return self

    def motor(self, side: int):
        import cotask, motor

        if self.is_built:
            self.fail()
        if not self.shares.is_built:
            self.shares.build()
        task = cotask.Task(
            motor.Motor(side).task,
            "Left Motor Task",
            priority=40,
            period=10,
            profile=True,
            shares=(
                self.shares.control_flag,
                self.shares.yaw_velocity_share,
                (
                    self.shares.left_motor_position_reset_flag
                    if side == Vehicle_Side.LEFT
                    else self.shares.right_motor_position_reset_flag
                ),
                (
                    self.shares.left_motor_position_share
                    if side == Vehicle_Side.LEFT
                    else self.shares.right_motor_position_share
                ),
            ),
        )
        if side == Vehicle_Side.LEFT:
            self.left_motor_task = task
        else:
            self.right_motor_task = task
        self.append(task)
        return self

    def course(self):
        import cotask, course

        if self.is_built:
            self.fail()
        if not self.shares.is_built:
            self.shares.build()
        self.course_task = cotask.Task(
            course.task,
            "Course",
            priority=100,
            period=50,
            profile=True,
            shares=(
                self.shares.control_flag,
                self.shares.motor_control_state_share,
                self.shares.target_heading_share,
                self.shares.left_motor_position_share,
                self.shares.right_motor_position_share,
                self.shares.heading_share,
                self.shares.centroid_stdev_share,
                self.shares.left_motor_position_reset_flag,
                self.shares.right_motor_position_reset_flag,
            ),
        )
        self.append(self.course_task)
        return self

    def append(self, task: cotask.Task):
        if task not in self.task_list:
            self.task_list.append(task)

    def all(self):
        if not self.shares.is_built:
            self.shares.build()
        self.vehicle_conrol().motor(Vehicle_Side.LEFT).motor(
            Vehicle_Side.RIGHT
        ).line_sensor().imu().course()
        return self

    def build(self):
        import cotask

        for task in self.task_list:
            if task not in cotask.task_list.pri_list:
                cotask.task_list.append(task)

    def run(self):
        import cotask

        if not self.is_built:
            self.build()
        while True:
            cotask.task_list.pri_sched()

    def fail(self):
        raise BaseException(
            "TaskShare has already been built, are you trying to run more than one control function"
        )


task_builder = TaskBuilder()
