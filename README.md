# Run this command to set up your dev enviroment
pip install -r requirements-dev.txt --target typings

#https://prod.liveshare.vsengsaas.visualstudio.com/join?A10C55ECDC63455E834136182A631351C6EA

# Romi Line-Following Robot

## Overview
This project is a line-following robot using a Romi chassis, an STM32-based Nucleo board, and sensors for autonomous navigation.

## Hardware & Software Used
- **Microcontroller**: Nucleo STM32-L476RG
- **Sensors**: QTR-HD-13A Reflectance Array, BNO055 IMU, Bump Sensors
- **Programming Language**: Python (MicroPython)
- **Motor Drivers**: Romi Motor Control System

## System Architecture
The software is based on **finite state machines (FSMs)** and **task scheduling** to efficiently control the robot. 

### Task Diagram
![Task Diagram](docs/task_diagram.png)

## Code Structure
- `main.py`: Runs the core task scheduler.
- `motor_control_task.py`: Handles motor speed adjustments.
- `line_sensor.py`: Reads and processes line sensor data.
- `bno055.py`: Communicates with the BNO055 IMU.
- `bump_sensors.py`: Detects collisions and obstacles.
- `HAL.py`: Initializes all hardware components.

## Results & Challenges
- The robot was successfully able to follow the line, but adjustments to PID tuning were required.
- Shiny surfaces presented difficulties in sensor readings, which were resolved with **super sampling**.
- Integrating bump sensors for obstacle avoidance improved the robot’s ability to navigate around objects.

## Video Demonstration
INSERT LINK HERE

