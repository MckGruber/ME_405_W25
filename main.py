from prelude import *
import HAL, motor_control_task, userbutton, utime, pyb, motor, bno055, line_sensor, course, tasks
import task_share, cotask


def run(fun, *args):
    try:
        fun(args)
        if len(cotask.task_list.pri_list) > 0:
            tasks.task_builder.run()
    except KeyboardInterrupt:
        print("\nTerminating Program")
        HAL.__MOTOR_LEFT__.ENABLE.low()
        HAL.__MOTOR_RIGHT__.ENABLE.low()
        print(cotask.task_list)

    except BaseException as e:
        HAL.__MOTOR_LEFT__.ENABLE.low()
        HAL.__MOTOR_RIGHT__.ENABLE.low()
        print(cotask.task_list)
        with open("log.txt", "a+") as log:
            try:
                print(e)
                print(e, file=log)
            except:
                print(e, file=log)


def main(in_run=False):
    if not in_run:
        run(main, True)
        return
    ## ------------------------ <Tasks> ------------------------ ##
    tasks.task_builder.all()

    ## ------------------------ </Tasks> ------------------------ ##

    return


def line_sensor_test(in_run=False):
    if not in_run:
        run(line_sensor_test, True)
        return
    while True:
        print([channel.read() for channel in HAL.__LINE_SENSOR__.CHANNELS])


def test_imu(in_run=False):
    if not in_run:
        run(test_imu, True)
        return
    imu = bno055.BNO055()  # Initialize the IMU using HAL-configured I2C
    import pyb

    print("\n[BNO055] Checking Calibration Status...")
    imu.calibrate_if_needed()  # Load calibration or start manual calibration

    print("\n[BNO055] IMU is ready! Printing Euler angles...\n")
    pyb.delay(1000)

    try:
        while True:
            heading, pitch, roll = imu.get_euler_angles()
            sys, gyro, accel, mag = imu.get_calibration_status()

            print(
                f"Euler Angles - Heading: {heading:.2f}, Pitch: {pitch:.2f}, Roll: {roll:.2f}"
            )
            print(
                f"Calibration Status - System: {sys}, Gyro: {gyro}, Accel: {accel}, Mag: {mag}\n"
            )

            pyb.delay(500)  # Delay between readings

    except KeyboardInterrupt:
        print("\n[BNO055] IMU Test Stopped.")


def I2C_test(in_run=False):
    if not in_run:
        run(I2C_test, True)
        return
    print(HAL._PB8)
    print(HAL._PB9)
    iic = pyb.I2C(1)
    iic = pyb.I2C(1, pyb.I2C.CONTROLLER)
    iic.init(pyb.I2C.CONTROLLER)
    print(iic)
    addrs = []
    while addrs == []:
        addrs = iic.scan()
        print(addrs)
    # for i in range(100):
    #     print(f'addr: {i} | is_ready: {iic.is_ready(i)}')
    #     utime.sleep_ms(100)


def motor_characterization(in_run=False):
    if not in_run:
        run(motor_characterization, True)
        return
    from collector import Collector

    for i in range(15, 0, -1):
        print(f"run in {i}")
        utime.sleep(1)
    Collector.run()
    return


def motor_test(test_pwm_percent: int, in_run=False):
    if not in_run:
        run(motor_test, test_pwm_percent, True)
        return
    print("Motor Test Start")
    import prelude

    if prelude.SPEED_SET_POINT != 0:
        prelude.SPEED_SET_POINT = 0

    left_motor_velocity_set_point_share = task_share.Share(
        "f", True, "Left Motor Velocity"
    )
    right_motor_velocity_set_point_share = task_share.Share(
        "f", True, "Right Motor Velocity"
    )
    shares = tasks.task_builder.shares.build()
    while shares.control_flag.get() == 0:
        continue
    while shares.control_flag.get() == 1:
        left_motor = motor.Motor(Vehicle_Side.LEFT)
        right_motor = motor.Motor(Vehicle_Side.RIGHT)
        left_motor.__hal__.PWM.pulse_width_percent(test_pwm_percent)
        right_motor.__hal__.PWM.pulse_width_percent(test_pwm_percent)
        left_motor.set_dir(MotorDirection.FWD)
        right_motor.set_dir(MotorDirection.REV)
        left_motor.enable()
        right_motor.enable()
        ticks = 0
        while ticks < 5:
            right_motor.encoder.update()
            left_motor.encoder.update()
            utime.sleep(0.5)
            ticks += 1
        left_velocity = left_motor.encoder.__velocity__
        right_velocity = right_motor.encoder.__velocity__
        left_motor.disable()
        right_motor.disable()
        print(
            f"for {test_pwm_percent}% PWN Pecent: Left Motor Velocity = {left_velocity}"
        )
        print(
            f"for {test_pwm_percent}% PWN Pecent: Right Motor Velocity = {right_velocity}"
        )
        left_motor_velocity_set_point_share.put(left_velocity)
        right_motor_velocity_set_point_share.put(right_velocity)
        left_motor_task = cotask.Task(
            left_motor.task,
            "Left Motor Task",
            priority=40,
            period=10,
            profile=True,
            shares=(
                shares.control_flag,
                left_motor_velocity_set_point_share,
                shares.left_motor_position_reset_flag,
                shares.left_motor_position_share,
            ),
        )

        right_motor_task = cotask.Task(
            motor.Motor(Vehicle_Side.RIGHT).task,
            "Right Motor Task",
            priority=40,
            period=10,
            profile=True,
            shares=(
                shares.control_flag,
                right_motor_velocity_set_point_share,
                shares.right_motor_position_reset_flag,
                shares.right_motor_position_share,
            ),
        )
        cotask.task_list.append(right_motor_task)
        cotask.task_list.append(left_motor_task)
        while True:
            cotask.task_list.rr_sched()
    return


def follow_line_test(in_run=False):
    if not in_run:
        run(follow_line_test, True)
        return
    tasks.task_builder.motor(Vehicle_Side.LEFT).motor(
        Vehicle_Side.RIGHT
    ).vehicle_conrol().line_sensor()
    tasks.task_builder.shares.motor_control_state_share.put(
        motor_control_task.MotorControl.S1_LINE_PID_CALC
    )
    return


if __name__ == "__main__":
    print(f"Voltage: {get_voltage()}")
    print(f"Speed Set Point: {SPEED_SET_POINT}")
    print(f"Estimated PWM Percent: {MOTOR_SET_POINT_PERCENT}")
    # main()
