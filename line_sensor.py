import HAL
import task_share
from prelude import *
import pyb
import array
import utime
import math


class LineSensor:
    # Define finite state machine (FSM) states
    S0_CALIBRATING = 0  # Calibration state
    S2_PROCESSING = 2  # Processing state

    SUPER_SAMPLE_COUNT = (
        10  # Number of samples per channel (is this too many or too little?)
    )

    def __init__(self):
        # Initialize the line sensor object

        self.sensors = (
            HAL.__LINE_SENSOR__.CHANNELS
        )  # Ensure CHANNELS is a list of sensor objects
        self.calibration_min = [4095] * len(
            self.sensors
        )  # Initial high values for calibration (min)
        self.calibration_max = [0] * len(
            self.sensors
        )  # Initial low values for calibration (max)
        self.state = self.S2_PROCESSING  # Start in the Processing state
        self.calibration_samples = 100  # Total number of calibration samples required
        self.calibration_data: list[tuple[float, float]] = []
        self.sample_count = 0  # Counter for calibration samples taken
        self.centroid = None  # Last computed centroid value
        self.timer = pyb.Timer(6, period=0xFFFF, prescaler=0)
        self.buff: int = 0
        from os import listdir

        filelist = listdir()
        if "IR_cal.txt" not in filelist:
            self.calibrate_step()
        else:
            self.load_calibration()

    def read_sampled(self, sensor: pyb.ADC):
        # Read and average ADC values from the sensor

        ## Moved to the class object, no need to initilize this bitch every 10ms
        # buf = array.array(
        #     "H", range(self.SUPER_SAMPLE_COUNT)
        # )  # Buffer for ADC readings

        self.buff = 0
        for _i in range(self.SUPER_SAMPLE_COUNT):
            self.buff += sensor.read()
            ## Should be uneeded, as wating takes a minimum of 6.5 ms of the 10ms of the period.
            # utime.sleep_us(
            #     1
            # )  # Unsure about this one, this will read using Timer 6 at 20kHz (0.05ms)
        return self.buff / self.SUPER_SAMPLE_COUNT  # Return the averaged value

    # Time: N/A - Not run in a task
    def calibrate_step(self):
        # Calibration step to update min/max values for each sensor
        continue_min = input("Place on White. Ready to continue [Y]/N: ")
        if continue_min == "N":
            raise BaseException("Calibration Stopped")
        data_min = [self.read_sampled(sensor) for sensor in self.sensors]

        continue_max = input("Place on Black. Ready to continue [Y]/N: ")
        if continue_max == "N":
            raise BaseException("Calibration Stopped")
        data_max = [self.read_sampled(sensor) for sensor in self.sensors]

        # Save calibration data
        with open("IR_cal.txt", "wt+") as f:
            data = list(zip(data_max, data_min))
            print(data, file=f)
            self.calibration_data = data

    # Time: N/A - Not run in a task
    def load_calibration(self):
        # Load calibration data from file
        with open("IR_cal.txt", "r") as f:
            self.calibration_data = list(
                filter(
                    lambda item: item != "",
                    map(
                        lambda str_list: (float(str_list[0]), float(str_list[1])),
                        filter(
                            lambda item: item != "",
                            map(
                                lambda item_str: item_str.split("(")[1].split(","),
                                filter(
                                    lambda item: item != "",
                                    f.readline().split("[")[1].split("]")[0].split(")"),
                                ),
                            ),
                        ),
                    ),
                )
            )
        if any(
            item[0] > 4095 or item[0] < 0 or item[1] > 4095 or item[1] < 0
            for item in self.calibration_data
        ):
            import os

            print("Calibration Data Out of bounds")
            os.remove("IR_cal.txt")
            self.calibrate_step()
        print(self.calibration_data)

    def calculate_centroid(self) -> tuple[float, float]:
        # Calculate the centroid based on sensor readings and calibration data
        values = [
            clamp(
                self.read_sampled(sensor),
                self.calibration_data[i][1],
                self.calibration_data[i][0],
            )
            for (i, sensor) in enumerate(self.sensors)
        ]
        centroid = sum([value * (i - 6) for (i, value) in enumerate(values)])
        average = sum(values) / len(values)
        stdev = math.sqrt(sum([(val - average) ** 2 for val in values]) / len(values))
        if DEBUG:
            print(
                " | ".join(
                    [
                        f"Centroid Error: {centroid}",
                        f"Average: {average}",
                        f"Standard Deviation: {stdev}",
                    ]
                )
            )
        return (centroid, stdev)

    def task(self, shares):
        # Task to continuously update the centroid value
        control_flag: task_share.Share
        centroid_share: task_share.Share
        centroid_stdev_share: task_share.Share
        (control_flag, centroid_share, centroid_stdev_share) = shares  # Shared variable
        while True:
            if control_flag.get() == 0:
                yield self.state
            else:
                # print(f"LineSensor")
                centroid, stdev = self.calculate_centroid()  # Update the centroid
                centroid_share.put(centroid)
                centroid_stdev_share.put(stdev)
                # print(f"Centroid: {centroid_share.get()}")
                yield self.state
