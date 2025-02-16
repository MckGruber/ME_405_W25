import utime
import cotask
from motor import Motor
from prelude import Vehicle_Side

def motor_control_task(shares=None):
    # Initialize motor objects for the left and right motors
    motor_left = Motor(Vehicle_Side.LEFT)
    motor_right = Motor(Vehicle_Side.RIGHT)
    
    # Define a list of speedsfrom 100 down to 0 in steps of 10
    speeds = list(range(100, -10, -10))  # [100, 90, 80, ..., 0]
    speed_index = 0
    # Duration (in milliseconds) to hold each speed command
    duration_ms = 5000      # Modify as needed
    start_time = utime.ticks_ms()

    while True:
        current_time = utime.ticks_ms()
        elapsed = utime.ticks_diff(current_time, start_time)
        
        # Check if the current speed should change
        if elapsed >= duration_ms:
            speed_index = (speed_index + 1) % len(speeds)
            start_time = current_time
        
        current_speed = speeds[speed_index]
        # Set the motor effort for both motors
        motor_left.effort(current_speed)
        motor_right.effort(current_speed)
        # Ensure the motors are enabled
        motor_left.enable()
        motor_right.enable()
        
        # Yield control to allow other tasks to run
        yield 0
