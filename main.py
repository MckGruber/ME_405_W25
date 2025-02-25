from prelude import *
import HAL, motor_control_task, userbutton, utime, pyb
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

def main():
    try:
        # Create shared variable for centroid data
        centroid_share = task_share.Share('f', True, "Centroid")

        # Get shared control flag from userbutton.py
        control_flag = userbutton.get_control_flag_share()

        # Create an IMU Angle Share
        heading_share = task_share.Share('f', True, "Heading Angle")
        pitch_share = task_share.Share('f', True, "Pitch Angle")
        roll_share = task_share.Share('f', True, "Roll Angle")

        # Create an IMU Velocity Share
        gyro_x_share = task_share.Share('f', True, "X Angular Velocity")
        gyro_y_share = task_share.Share('f', True, "Y Angular Velocity")
        gyro_z_share = task_share.Share('f', True, "Z Angular Velocity")

        # Target Heading Share
        target_heading_share = task_share.Share('f', True, "Target Heading")

        # Create tasks with shared control_flag
        motor_task = cotask.Task(motor_control_task.MotorControl.task, name="MotorControl",
                                 priority=20, period=30, profile=True, trace=True,
                                 shares=(centroid_share, heading_share, pitch_share,
                                       roll_share, gyro_x_share, gyro_y_share,
                                       gyro_z_share, control_flag, target_heading_share))
        # coll_task = cotask.Task(collector_task.collector_task, name="Collector",
        #                         priority=1000, period=10, profile=True)
        line_task = cotask.Task(LineSensor().task, name="LineSensor",
                                priority=30, period=30, profile=True, trace=True,
                                shares=(centroid_share))
        # garbage_collector_task = cotask.Task(me_gc, name="Garbage Collection", priority=1000, period=100, profile=True, trace=True)
        # status_task = cotask.Task(status_print, name="Status Print", priority=1000, period=500, profile=False, trace=True)
        
        imu_task = cotask.Task(BNO055().task, name="IMU",
                               priority=10, period=30, profile=True, trace=True,
                               shares=(centroid_share, heading_share, pitch_share,
                                       roll_share, gyro_x_share, gyro_y_share,
                                       gyro_z_share, control_flag, target_heading_share))

        
        # Add tasks to the task list
        cotask.task_list.append(motor_task)
        # cotask.task_list.append(coll_task)
        cotask.task_list.append(line_task)
        cotask.task_list.append(imu_task)
        # cotask.task_list.append(status_task)
        # cotask.task_list.append(garbage_collector_task)
        # cotask.task_list

        # Enable the motors by running the scheduler
        target_heading_share.put(0.0)
        while True:
            # print(cotask.task_list)
            cotask.task_list.pri_sched()

    except KeyboardInterrupt:
        print("\nTerminating Program")
        HAL.__MOTOR_LEFT__.ENABLE.low()
        HAL.__MOTOR_RIGHT__.ENABLE.low()
        return

    except BaseException as e:
        HAL.__MOTOR_LEFT__.ENABLE.low()
        HAL.__MOTOR_RIGHT__.ENABLE.low()
        with open('log.txt', 'a+') as log:
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
            
            print(f"Euler Angles - Heading: {heading:.2f}, Pitch: {pitch:.2f}, Roll: {roll:.2f}")
            print(f"Calibration Status - System: {sys}, Gyro: {gyro}, Accel: {accel}, Mag: {mag}\n")
            
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


if __name__ == "__main__":
    # test_imu()
    # I2C_test()
    main()
