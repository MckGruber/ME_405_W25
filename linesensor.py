import pyb
import time
import HAL
import task_share, cotask

class LineSensor:
    # Define finite state machine (FSM) states
    S0_CALIBRATING = 0  # State when the sensor is gathering calibration data (min/max values)
    S1_READING = 1      # State when the sensor is ready to take a reading
    S2_PROCESSING = 2   # State when the sensor data is processed to compute the centroid

    def __init__(self):
        # Initialize the line sensor object
        self.sensors = HAL.__LINE_SENSOR__.CHANNELS         # Ensure CHANNELS is a list of sensor objects
        self.calibration_min = [4095] * 13                  # Initial high values for calibration (min)
        self.calibration_max = [0] * 13                     # Initial low values for calibration (max)
        self.state = self.S0_CALIBRATING                    # Start in the CALIBRATING state
        self.calibration_samples = 100                      # Total number of calibration samples required
        self.sample_count = 0                               # Counter for calibration samples taken
        self.centroid = None                                # Last computed centroid value

    def calibrate_step(self):
        # Calibration step to update min/max values for each sensor
        if self.sample_count < self.calibration_samples:
            # For each sensor, update calibration bounds based on the current reading
            for i, sensor in enumerate(self.sensors):
                reading = sensor.read()
                self.calibration_min[i] = min(self.calibration_min[i], reading)
                self.calibration_max[i] = max(self.calibration_max[i], reading)
            self.sample_count += 1  # Increment the calibration sample counter
        else:
            # Once enough samples have been collected, finish calibration
            print("Calibration complete.")
            self.state = self.S1_READING  # Transition to the READING state

    def read_raw(self):
        # Read raw sensor values from each sensor
        return [sensor.read() for sensor in self.sensors]

    def read_normalized(self):
        # Read normalized sensor values from each sensor
        raw_values = self.read_raw()
        normalized = []
        for i, value in enumerate(raw_values):
            min_val = self.calibration_min[i]
            max_val = self.calibration_max[i]
            if max_val > min_val:
                normalized_value = (value - min_val) * 1000 // (max_val - min_val)
                normalized.append(min(max(normalized_value, 0), 1000))
            else:
                normalized.append(0)
        return normalized

    def calculate_centroid(self) -> float | None:
        # Calculate the centroid value from the normalized sensor
        normalized_values = self.read_normalized()
        total_weight = sum(normalized_values)
        if total_weight == 0:
            return None  # No line detected if all sensors are inactive
        return sum(i * normalized_values[i] for i in range(len(normalized_values))) / total_weight

    @classmethod
    def task(cls, shares):
        # Task function to run the line sensor FSM
        centroid_share = shares[0]  # Shared variable to store the centroid value for other tasks
        line_sensor = cls()

        # Main loop for the line sensor task
        while True:
            # FSM: Determine action based on the current state
            if line_sensor.state == line_sensor.S0_CALIBRATING:
                # CALIBRATING: Collect calibration samples to update sensor min/max values.
                line_sensor.calibrate_step()
                # (Optional) Log calibration progress here if needed.

            elif line_sensor.state == line_sensor.S1_READING:
                # READING: Transition state to prepare for processing the sensor data.
                line_sensor.state = line_sensor.S2_PROCESSING

            elif line_sensor.state == line_sensor.S2_PROCESSING:
                # PROCESSING: Calculate the centroid from sensor readings.
                line_sensor.centroid = line_sensor.calculate_centroid()
                # Update the shared variable with the new centroid value
                centroid_share.put(line_sensor.centroid)
                # After processing, return to the READING state for the next cycle.
                line_sensor.state = line_sensor.S1_READING

            # Yield control so the scheduler can run other tasks
            yield
