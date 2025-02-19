#**THIS MODULE IS NOT NEEDED**

















# import pyb
# from HAL import __BLUE_TOOTH__

# class Bluetooth:    
#     def __init__(self, baudrate=115200, timeout=1000):
#         # Set the baudrate and timeout for the UART object.
#         self.baudrate = baudrate
#         self.timeout = timeout
#         # Create the UART object on the channel specified in HAL for Bluetooth.
#         self.uart = pyb.UART(1, 115200, timeout = 100)
#         # Enable the Bluetooth module by setting the ENABLE pin high.

#         ##* THIS IS NOT NEEDEd
#         # __BLUE_TOOTH__.ENABLE.high()

#         # Read the initial state from the STATE pin.
#         self.state = __BLUE_TOOTH__.STATE.value()
    
#     def send(self, data):
#         # If the data is a string, convert it to bytes.
#         if isinstance(data, str):
#             data = data.encode('utf-8')
#         self.uart.write(data)
    
#     def recv(self, num_bytes=64):
#         # Check if there are bytes available to read.
#         if self.uart.any():
#             return self.uart.read(num_bytes)
#         return None
    
#     def send_at_command(self, command):
#         # Append carriage return and newline to the command.
#         full_cmd = command + "\r\n"
#         self.send(full_cmd)
#         # Wait briefly to allow the module to respond.
#         pyb.delay(100)
#         response = self.recv(128)
#         if response:
#             return response.decode('utf-8', 'ignore')
#         return ""
    
#     def is_connected(self):
#         # Read the state from the STATE pin.
#         return __BLUE_TOOTH__.STATE.value() == 1
    
#     def set_baudrate(self, new_baudrate):
#         # Update the UART object with the new baudrate.
#         self.baudrate = new_baudrate
#         self.uart.init(new_baudrate, timeout=self.timeout)

#     def __del__(self):         
#           # Disable the Bluetooth module by setting the ENABLE pin low.

#           ##* THIS IS NOT NEEDED
#         #   __BLUE_TOOTH__.ENABLE.low()

#           # Close the UART object.
#           self.uart.deinit()
#           print("Bluetooth disabled.")
