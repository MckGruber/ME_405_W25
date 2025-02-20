import pyb
import time
import HAL
import task_share, cotask
from prelude import *

class LineSensor:
    # Define finite state machine (FSM) states
    S0_CALIBRATING = 0  # State when the sensor is gathering calibration data (min/max values)
    S2_PROCESSING = 2   # State when the sensor data is processed to compute the centroid

    def __init__(self):
        # Initialize the line sensor object
        self.sensors = HAL.__LINE_SENSOR__.CHANNELS         # Ensure CHANNELS is a list of sensor objects
        self.calibration_min = [4095] * 13                  # Initial high values for calibration (min)
        self.calibration_max = [0] * 13                     # Initial low values for calibration (max)
        self.state = self.S0_CALIBRATING                    # Start in the CALIBRATING state
        self.calibration_samples = 100                      # Total number of calibration samples required
        self.calibration_data: list[tuple[float, float]] = []
        self.sample_count = 0                               # Counter for calibration samples taken
        self.centroid = None                                # Last computed centroid value

    def calibrate_step(self):
        # Calibration step to update min/max values for each sensor
        # if self.sample_count < self.calibration_samples:
        #     # For each sensor, update calibration bounds based on the current reading
        #     for i, sensor in enumerate(self.sensors):
        #         reading = sensor.read()
        #         # self.calibration_min[i] = min(self.calibration_min[i], reading)
        #         # self.calibration_max[i] = max(self.calibration_max[i], reading)
        #     self.sample_count += 1  # Increment the calibration sample counter
        # else:
        #     # Once enough samples have been collected, finish calibration
        #     print("Calibration complete.")
        #     self.state = self.S1_READING  # Transition to the READING state
        continue_min = input("Place on White. Ready to continue [Y]/N: ")
        if continue_min == "N":
            raise BaseException("Calibration Stopped")
        data_min = []
        for sensor in self.sensors:
            sensor_values = []
            while len(sensor_values) < self.calibration_samples:
                sensor_values.append(sensor.read())
            data_min.append(sum(sensor_values) / len(sensor_values))
        continue_max = input("Place on Black. Ready to continue [Y]/N: ")
        print(continue_max)
        if continue_max == "N":
            raise BaseException("Calibration Stopped")
        data_max = []
        for sensor in self.sensors:
            sensor_values = []
            while len(sensor_values) < self.calibration_samples:
                sensor_values.append(sensor.read())
            data_max.append(sum(sensor_values) / len(sensor_values))
        with open("IR_cal.txt", "wt+") as f:
            data = list(zip(data_max, data_min))
            print(data)
            print(data, file=f)
            self.calibration_data = data


    def calculate_centroid(self) -> float:
        # Read normalized sensor values from each sensor
        normalized: list[float] = []
        # for i, value in enumerate(raw_values):
        #     min_val = self.calibration_min[i]
        #     max_val = self.calibration_max[i]
        #     if max_val > min_val:
        #         normalized_value = (value - min_val) * 1000 // (max_val - min_val)
        #         normalized.append(min(max(normalized_value, 0), 1000))
        #     else:
        #         normalized.append(0)
        weight = -6
        for i, sensor in enumerate(self.sensors):
            value = sensor.read()
            min_val = self.calibration_data[i][1]
            max_val = self.calibration_data[i][0]
            val = clamp(value, min_val, max_val)
            normalized.append(((val-min_val)/(max_val - min_val)) * weight)
            weight += 1
        return sum(normalized)

    @classmethod
    def task(cls, shares):
        # Task function to run the line sensor FSM
        # print(shares)
        centroid_share = shares  # Shared variable to store the centroid value for other tasks
        line_sensor = cls()

        # Main loop for the line sensor task
        while True:
            
            # FSM: Determine action based on the current state
            if line_sensor.state == line_sensor.S0_CALIBRATING:
                from os import listdir
                filelist = listdir()
                if "IR_cal.txt" not in filelist:

                    # CALIBRATING: Collect calibration samples to update sensor min/max values.
                    line_sensor.calibrate_step()
                    # (Optional) Log calibration progress here if needed.
                else:
                    if line_sensor.calibration_data == []:
                        with open("IR_cal.txt", "r") as f:
                            line_sensor.calibration_data = list(filter(lambda item: item != '', map(lambda str_list: (float(str_list[0]), float(str_list[1])), filter(lambda item: item != '', map(lambda item_str: item_str.split("(")[1].split(","), filter(lambda item: item != '', f.readline().split("[")[1].split("]")[0].split(")")))))))
                            # line: str = f.readline()
                            # split_one = list(filter(lambda item: item != '', line.split("[")[1].split("]")[0].split(")")))
                            # print(f'Split One: {split_one}')
                            # split_two = list(filter(lambda item: item != '', map(lambda item_str: item_str.split("(")[1].split(","), split_one)))
                            # print(f'Split Two: {split_two}')
                            # split_three = list(filter(lambda item: item != '', map(lambda str_list: (float(str_list[0]), float(str_list[1])), split_two)))
                            # print(f'Split Three: {split_three}')
                            # line_sensor.calibration_data = split_three
                    line_sensor.state = line_sensor.S2_PROCESSING
                yield line_sensor.state

            elif line_sensor.state == line_sensor.S2_PROCESSING:
                # PROCESSING: Calculate the centroid from sensor readings.
                line_sensor.centroid = line_sensor.calculate_centroid()
                # print(line_sensor.centroid)
                # Update the shared variable with the new centroid value
                centroid_share.put(line_sensor.centroid)
                # After processing, return to the READING state for the next cycle.
                yield line_sensor.state
            else:
                line_sensor.state = line_sensor.S2_PROCESSING
                yield line_sensor.state
