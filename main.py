from prelude import *
import HAL, motor_control_task, userbutton, utime, pyb, motor
from linesensor import LineSensor
import task_share, cotask
from nb_input import NB_Input
import gc
from bno055 import BNO055


def status_print():
    while True:
        print("")
        print(cotask.task_list)
        gc.collect()
        yield


def echo_task(shares: tuple[task_share.Queue, NB_Input]):
    buffer = shares[0]
    nb_in = shares[1]
    chars_written = 0
    while buffer.any():
        print(chr(buffer.get()), end="")
        chars_written += 1
    print()
    chars_written += 1
    print(">>", end="")
    chars_written += 2
    for char in nb_in._line:
        print(char, end="")
        chars_written += 1
    print("\r" * chars_written)
    chars_written = 0
    if nb_in.any():
        eval(nb_in.get())  # type: ignore


def main():
    try:
        # Create shared variable for centroid data
        centroid_share = task_share.Share("f", True, "Centroid")

        # Get shared control flag from userbutton.py
        control_flag = userbutton.get_control_flag_share()

        # Create an IMU Angle Share
        heading_share = task_share.Share("f", True, "Heading Angle")
        pitch_share = task_share.Share("f", True, "Pitch Angle")
        roll_share = task_share.Share("f", True, "Roll Angle")

        # Create an IMU Velocity Share
        gyro_x_share = task_share.Share("f", True, "X Angular Velocity")
        gyro_y_share = task_share.Share("f", True, "Y Angular Velocity")
        gyro_z_share = task_share.Share("f", True, "Z Angular Velocity")

        # Target Heading Share
        target_heading_share = task_share.Share("f", True, "Target Heading")

        # Motor Velocity Share
        left_motor_velocity_share = task_share.Share("f", True, "Left Motor Velocity")
        right_motor_velocity_share = task_share.Share("f", True, "Right Motor Velocity")

        # Create tasks with shared control_flag
        motor_task = cotask.Task(
            motor_control_task.MotorControl.task,
            name="MotorControl",
            priority=20,
            period=30,
            profile=True,
            trace=True,
            shares=(
                centroid_share,
                heading_share,
                pitch_share,
                roll_share,
                gyro_x_share,
                gyro_y_share,
                gyro_z_share,
                control_flag,
                target_heading_share,
                left_motor_velocity_share,
                right_motor_velocity_share,
            ),
        )

        line_task = cotask.Task(
            LineSensor().task,
            name="LineSensor",
            priority=30,
            period=30,
            profile=True,
            trace=True,
            shares=(centroid_share),
        )

        imu_task = cotask.Task(
            BNO055().task,
            name="IMU",
            priority=10,
            period=30,
            profile=True,
            trace=True,
            shares=(
                centroid_share,
                heading_share,
                pitch_share,
                roll_share,
                gyro_x_share,
                gyro_y_share,
                gyro_z_share,
                control_flag,
                target_heading_share,
            ),
        )

        left_motor_task = cotask.Task(
            motor.Motor(Vehicle_Side.LEFT).task,
            "Left Motor Task",
            priority=40,
            period=10,
            profile=True,
            shares=(left_motor_velocity_share),
        )

        right_motor_task = cotask.Task(
            motor.Motor(Vehicle_Side.RIGHT).task,
            "Right Motor Task",
            priority=40,
            period=10,
            profile=True,
            shares=(right_motor_velocity_share),
        )

        # Add tasks to the task list
        cotask.task_list.append(motor_task)
        cotask.task_list.append(line_task)
        cotask.task_list.append(imu_task)
        cotask.task_list.append(right_motor_task)
        cotask.task_list.append(left_motor_task)

        # Enable the motors by running the scheduler
        target_heading_share.put(0.0)
        while True:
            # print(cotask.task_list)
            cotask.task_list.pri_sched()

    except KeyboardInterrupt:
        print("\nTerminating Program")
        HAL.__MOTOR_LEFT__.ENABLE.low()
        HAL.__MOTOR_RIGHT__.ENABLE.low()
        print(cotask.task_list)
        return

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
    return


def line_sensor_test():
    while True:
        print([channel.read() for channel in HAL.__LINE_SENSOR__.CHANNELS])


def test_imu():
    imu = BNO055()  # Initialize the IMU using HAL-configured I2C
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


def I2C_test():
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


def motor_characterization():
    try:
        from collector import Collector

        for i in range(15, 0, -1):
            print(f"run in {i}")
            utime.sleep(1)
        Collector.run()
    except KeyboardInterrupt:
        print("\nTerminating Program")
        HAL.__MOTOR_LEFT__.ENABLE.low()
        HAL.__MOTOR_RIGHT__.ENABLE.low()
        print(cotask.task_list)
        return

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
    return


if __name__ == "__main__":
    # test_imu()
    # I2C_test()
    # main()
    motor_characterization()
