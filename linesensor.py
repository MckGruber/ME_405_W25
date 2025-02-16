import pyb
import time

class LineSensor:
    def __init__(self, adc_pins):
        """
        Initializes the LineSensor class with a list of ADC pins.
        :param adc_pins: List of integers representing the ADC pin numbers.
        """
        self.sensors = [pyb.ADC(pyb.Pin(pin)) for pin in adc_pins]
        self.calibration_min = [4095] * len(adc_pins)
        self.calibration_max = [0] * len(adc_pins)

    def calibrate(self, samples=100):
        """
        Calibrates the sensors by taking multiple readings and recording the min and max values.
        :param samples: Number of samples to take for calibration.
        """
        print("Calibrating sensors...")
        for _ in range(samples):
            for i, sensor in enumerate(self.sensors):
                reading = sensor.read()
                self.calibration_min[i] = min(self.calibration_min[i], reading)
                self.calibration_max[i] = max(self.calibration_max[i], reading)
            time.sleep(0.01)
        print("Calibration complete.")

    def read_raw(self):
        """
        Reads raw values from the sensors.
        :return: List of raw sensor values.
        """
        return [sensor.read() for sensor in self.sensors]

    def read_normalized(self):
        """
        Reads normalized values from the sensors.
        :return: List of normalized sensor values between 0 and 1000.
        """
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

    def calculate_centroid(self):
        """
        Calculates the centroid of the line position based on normalized sensor values.
        :return: Centroid index (float) indicating the line position.
        """
        normalized_values = self.read_normalized()
        total_weight = sum(normalized_values)
        if total_weight == 0:
            return None  # No line detected
        centroid = sum(i * normalized_values[i] for i in range(len(normalized_values))) / total_weight
        return centroid

    def print_status(self):
        """
        Prints the current status of the sensor readings for debugging.
        """
        raw = self.read_raw()
        normalized = self.read_normalized()
        centroid = self.calculate_centroid()
        print(f"Raw: {raw}")
        print(f"Normalized: {normalized}")
        print(f"Centroid: {centroid}")