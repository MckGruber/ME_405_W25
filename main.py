from prelude import *
from collector import Collector
import HAL
import cotask
import task_share
import motor_control_task
import collector_task


def main():
  try:
    # Create task objects with desired priority and period
    motor_task = cotask.Task(motor_control_task.motor_control_task, name="MotorControl", priority=2, period=50, profile=True)
    coll_task = cotask.Task(collector_task.collector_task, name="Collector", priority=1, period=10, profile=True)

    # Add tasks to the task list
    cotask.task_list.append(motor_task)
    cotask.task_list.append(coll_task)

    # file_names = Collector.run()
    # HAL.__MOTOR_LEFT__.ENABLE.low()
    # HAL.__MOTOR_RIGHT__.ENABLE.low()
    # for file_name in file_names:
    #   with open(file_name, "r") as f:
    #     print(f'{file_name}: \n\r{f.read()}')
  
    # Run the scheduler in an infinite loop
    while True:
        cotask.task_list.pri_sched()

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


if __name__ == "__main__":
  main()