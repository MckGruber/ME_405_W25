from prelude import *
import HAL, motor_control_task
from task_share import Share, Queue


def get_relative_angle(angle: int | None, starting_angle: int) -> int:
    # if angle == 0, relative angle = 0 - starting angle
    #   if 0 - starting angle > 0
    #   else 0 - starting angle + 5670
    if angle == None:
        angle = int(input("Enter a Heading (16th of a degree)"))
        print(angle)
    return (
        angle - starting_angle
        if angle - starting_angle > 0
        else angle - starting_angle + 5670
    )


def task(shares):
    control_flag_share: Share
    motor_control_state_share: Share
    target_heading_share: Share
    left_motor_position_share: Queue
    right_motor_position_share: Queue
    heading_share: Share
    centroid_stdev_share: Share
    left_motor_position_reset_flag: Share
    right_motor_position_reset_flag: Share

    (
        control_flag_share,
        motor_control_state_share,
        target_heading_share,
        left_motor_position_share,
        right_motor_position_share,
        heading_share,
        centroid_stdev_share,
        left_motor_position_reset_flag,
        right_motor_position_reset_flag,
    ) = shares
    starting_heading = 0
    state = 0
    while True:
        if control_flag_share.get() == 0:
            if state != 0:
                state = 0
            yield state
        else:
            ## State Map:
            # S0: Starting ==>
            # S5: Checkpoint 0 ==> Checkpoint 1
            # S10: Checkpoint 1 ==> Checkpoint 2
            # S20: Checkpoint 2 ==> Target 2
            # S30: Target 2 ==> Checkpoint 3
            # S40: Checkpoint 3 ==>
            # S50: Grid ==>
            # S55: Grid Middle Point ==>
            # S60: Target 1 ==>
            # S70: End ==>
            # S80: Restart ↩

            # """
            # S0: Starting:
            # while <all ir sensors are reading a value>:
            #     <drive straight following starting heading>
            # encoder_left.zero()
            # encoder_right.zero()
            # state = S5
            # """
            if state == 0:
                target_heading_share.put(heading_share.get())
                motor_control_state_share.put(
                    motor_control_task.MotorControl.S2_HEADING_PID_CALC
                )
                while centroid_stdev_share.get() >= STDEV_SET_POINT:
                    yield state
                left_motor_position_reset_flag.put(1)
                right_motor_position_reset_flag.put(1)
                starting_heading = heading_share.get()
                state = 5
            # '''
            # S5: Checkpoint One:
            #     while heading < starting_heading - 90°:
            #         motor_control_state ==> Line Following
            #     target_heading.put(starting_heading - 90°)
            #     motor_control_state ==> Heading Following
            #     while (<Left Motor Position> + <Right Motor Position>) / 2 < CHECKPOINT_ONE_DISTANCE_SET_POINT:
            #         yeild
            #     state = S10
            # '''
            elif state == 5:
                motor_control_state_share.put(
                    motor_control_task.MotorControl.S1_LINE_PID_CALC
                )
                target_heading_share.put(
                    get_relative_angle(
                        starting_heading - int(90 * 16), starting_heading
                    )
                )
                while (
                    get_relative_angle(heading_share.get(), starting_heading)
                    < target_heading_share.get()
                ):
                    yield state
                motor_control_state_share.put(
                    motor_control_task.MotorControl.S2_HEADING_PID_CALC
                )
                while (
                    left_motor_position_share.get() + right_motor_position_share.get()
                ) / 2 < S5_DISTANCE_SET_POINT:
                    yield state
                state = 10
            elif state == 10:
                motor_control_state_share.put(
                    motor_control_task.MotorControl.S1_LINE_PID_CALC
                )
                while (
                    left_motor_position_share.get() + right_motor_position_share.get()
                ) / 2 < S10_DISTANCE_SET_POINT:
                    yield state
                state = 20
            elif state == 20:
                target_heading_share.put(
                    get_relative_angle(S20_HEADING_SET_POINT, starting_heading)
                )
                motor_control_state_share.put(
                    motor_control_task.MotorControl.S2_HEADING_PID_CALC
                )
                while (
                    left_motor_position_share.get() + right_motor_position_share.get()
                ) / 2 < S20_DISTANCE_SET_POINT:
                    yield state
                state = 30
            elif state == 30:
                target_heading_share.put(
                    get_relative_angle(S30_HEADING_SET_POINT, starting_heading)
                )
                motor_control_state_share.put(
                    motor_control_task.MotorControl.S2_HEADING_PID_CALC
                )
                while (
                    left_motor_position_share.get() + right_motor_position_share.get()
                ) / 2 < S30_DISTANCE_SET_POINT:
                    yield state
            elif state == 40:
                motor_control_state_share.put(
                    motor_control_task.MotorControl.S1_LINE_PID_CALC
                )
                while (
                    left_motor_position_share.get() + right_motor_position_share.get()
                ) / 2 < S40_DISTANCE_SET_POINT:
                    yield state
                while centroid_stdev_share.get() <= STDEV_SET_POINT:
                    yield state
                state = 50
            elif state == 50:
                target_heading_share.put(
                    get_relative_angle(S50_HEADING_SET_POINT, starting_heading)
                )
                motor_control_state_share.put(
                    motor_control_task.MotorControl.S2_HEADING_PID_CALC
                )
                while (
                    left_motor_position_share.get() + right_motor_position_share.get()
                ) / 2 < S50_DISTANCE_SET_POINT:
                    yield state
                state = 55
            elif state == 55:
                target_heading_share.put(
                    get_relative_angle(S55_HEADING_SET_POINT, starting_heading)
                )
                while (
                    left_motor_position_share.get() + right_motor_position_share.get()
                ) / 2 < S55_DISTANCE_SET_POINT:
                    yield state
                state = 60
            elif state == 60:
                target_heading_share.put(
                    get_relative_angle(S60_HEADING_SET_POINT, starting_heading)
                )
                while (
                    left_motor_position_share.get() + right_motor_position_share.get()
                ) / 2 < S60_DISTANCE_SET_POINT:
                    yield state
                state = 70
            elif state == 70:
                target_heading_share.put(
                    get_relative_angle(S70_HEADING_SET_POINT, starting_heading)
                )
                while (
                    left_motor_position_share.get() + right_motor_position_share.get()
                ) / 2 < S70_DISTANCE_SET_POINT:
                    yield state
                state = 80
            elif state == 80:
                motor_control_state_share.put(
                    motor_control_task.MotorControl.S1_LINE_PID_CALC
                )
                while centroid_stdev_share.get() <= STDEV_SET_POINT:
                    yield state
                while centroid_stdev_share.get() >= STDEV_SET_POINT:
                    yield state
                control_flag_share.put(1)
                HAL.__MOTOR_LEFT__.ENABLE.low()
                HAL.__MOTOR_RIGHT__.ENABLE.low()
                print("Done")
            yield state
