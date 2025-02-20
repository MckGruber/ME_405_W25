from prelude import *
from collector import Collector
import HAL
import motor_control_task
import collector_task
import userbutton
from linesensor import LineSensor
import task_share
import cotask
# import BT_configurator

def main():
    try:
        # Create shared variable for centroid data
        centroid_share = task_share.Share('f', True, "Centroid")

        # Get shared control flag from userbutton.py
        control_flag = userbutton.get_control_flag_share()

        # Create tasks with shared control_flag
        motor_task = cotask.Task(motor_control_task.MotorControl.task, name="MotorControl",
                                 priority=2, period=10, profile=True, trace=True,
                                 shares=(centroid_share, control_flag))
        # coll_task = cotask.Task(collector_task.collector_task, name="Collector",
        #                         priority=1000, period=10, profile=True)
        line_task = cotask.Task(LineSensor.task, name="LineSensor",
                                priority=1, period=10, profile=True, trace=True,
                                shares=(centroid_share))

        # Add tasks to the task list
        cotask.task_list.append(motor_task)
        # cotask.task_list.append(coll_task)
        cotask.task_list.append(line_task)

        # Enable the motors by running the scheduler
        while True:
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

if __name__ == "__main__":
    print("waiting")
    while HAL._PC13.value():
        continue
    print("Starting")
    main()
