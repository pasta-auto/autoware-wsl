#!/usr/bin/python3
import os
import sys
import time
import signal   
import threading
import math

# Imports carla egg file
sys.path.append("%s/%s" % (os.getcwd(),"carlaPython/carla/dist/carla-0.9.14-py3.10-linux-x86_64.egg") )

import argparse

import curses
import curses.textpad
import carla 

from carla_msgs.msg import (
    CarlaEgoVehicleInfo,
    CarlaEgoVehicleInfoWheel,
    CarlaEgoVehicleControl,
    CarlaEgoVehicleStatus,
    CarlaEgoVehicleLight,
    CarlaEgoVehicleFailure
)

import rclpy
from std_msgs.msg import Float32
from autoware_auto_vehicle_msgs.msg import ControlModeReport, GearReport, SteeringReport, TurnIndicatorsReport, HazardLightsReport, VelocityReport, TurnIndicatorsCommand, HazardLightsCommand
from autoware_auto_control_msgs.msg import AckermannControlCommand

from ackermann_msgs.msg import AckermannDrive

# Position constants
# Lights
LIGHTS_COL_START = 1
LIGHTS_COL_END = LIGHTS_COL_START+ 21
LIGHTS_ROW_START = 1
LIGHTS_ROW_END = LIGHTS_ROW_START + 12

LIGHTS_A_COL = LIGHTS_COL_START + 12
LIGHTS_R_COL = LIGHTS_COL_START + 15
LIGHTS_S_COL = LIGHTS_COL_START + 18
LIGHTS_C_COL = LIGHTS_COL_START + 21

LIGHTS_POS_ROW = LIGHTS_ROW_START + 1
LIGHTS_LB_ROW = LIGHTS_ROW_START + 2
LIGHTS_HB_ROW = LIGHTS_ROW_START + 3
LIGHTS_BRAKE_ROW = LIGHTS_ROW_START + 4
LIGHTS_RTURN_ROW = LIGHTS_ROW_START + 5
LIGHTS_LTURN_ROW = LIGHTS_ROW_START + 6
LIGHTS_REV_ROW = LIGHTS_ROW_START + 7
LIGHTS_FOG_ROW = LIGHTS_ROW_START + 8
LIGHTS_INT_ROW = LIGHTS_ROW_START + 9
LIGHTS_SPECIAL1_ROW = LIGHTS_ROW_START + 10
LIGHTS_SPECIAL2_ROW = LIGHTS_ROW_START + 11
LIGHTS_HAZARD_ROW = LIGHTS_ROW_START + 12

# Steerin
STEER_COL_START = 25
STEER_COL_END = STEER_COL_START + 37
STEER_ROW_START = 1
STEER_ROW_END = STEER_ROW_START + 1

STEER_A_COL = STEER_COL_START + 8
STEER_R_COL = STEER_COL_START + 16
STEER_S_COL = STEER_COL_START + 24
STEER_C_COL = STEER_COL_START + 32

STEER_DATA_ROW = STEER_ROW_START + 1

# Speed
SPEED_COL_START = 25
SPEED_COL_END = SPEED_COL_START + 37
SPEED_ROW_START = 5
SPEED_ROW_END = SPEED_ROW_START + 1

SPEED_A_COL = SPEED_COL_START + 8
SPEED_R_COL = SPEED_COL_START + 16
SPEED_S_COL = SPEED_COL_START + 24
SPEED_C_COL = SPEED_COL_START + 32

SPEED_DATA_ROW = SPEED_ROW_START + 1

is_running = False

def main(stdscr):
    global is_running
    is_running = True

    global stdscr_g
    stdscr_g = stdscr

    setup(stdscr)
    
    dataLoop(stdscr)
def setup(stdscr):
    # Clear screen
    stdscr.clear()

    curses.curs_set(0)

    curses.textpad.rectangle(stdscr, LIGHTS_ROW_START - 1, LIGHTS_COL_START - 1, LIGHTS_ROW_END + 1, LIGHTS_COL_END + 1)
    curses.textpad.rectangle(stdscr, STEER_ROW_START - 1, STEER_COL_START - 1, STEER_ROW_END + 1, STEER_COL_END + 1)
    curses.textpad.rectangle(stdscr, SPEED_ROW_START - 1, SPEED_COL_START - 1, SPEED_ROW_END + 1, SPEED_COL_END + 1)

    # Lights
    stdscr.addstr(LIGHTS_ROW_START, LIGHTS_A_COL, "A", curses.A_BOLD)
    stdscr.addstr(LIGHTS_ROW_START, LIGHTS_R_COL, "R", curses.A_BOLD)
    stdscr.addstr(LIGHTS_ROW_START, LIGHTS_S_COL, "S", curses.A_BOLD)
    stdscr.addstr(LIGHTS_ROW_START, LIGHTS_C_COL, "C", curses.A_BOLD)
    stdscr.addstr(LIGHTS_POS_ROW, LIGHTS_COL_START, "Position", curses.A_BOLD)
    stdscr.addstr(LIGHTS_LB_ROW, LIGHTS_COL_START, "Low Beam", curses.A_BOLD)
    stdscr.addstr(LIGHTS_HB_ROW, LIGHTS_COL_START, "High Beam", curses.A_BOLD)
    stdscr.addstr(LIGHTS_BRAKE_ROW, LIGHTS_COL_START, "Brake", curses.A_BOLD)
    stdscr.addstr(LIGHTS_RTURN_ROW, LIGHTS_COL_START, "R Turn", curses.A_BOLD)
    stdscr.addstr(LIGHTS_LTURN_ROW, LIGHTS_COL_START, "L Turn", curses.A_BOLD)
    stdscr.addstr(LIGHTS_REV_ROW, LIGHTS_COL_START, "Reverse", curses.A_BOLD)
    stdscr.addstr(LIGHTS_FOG_ROW, LIGHTS_COL_START, "Fog", curses.A_BOLD)
    stdscr.addstr(LIGHTS_INT_ROW, LIGHTS_COL_START, "Interior", curses.A_BOLD)
    stdscr.addstr(LIGHTS_SPECIAL1_ROW, LIGHTS_COL_START, "Special 1", curses.A_BOLD)
    stdscr.addstr(LIGHTS_SPECIAL2_ROW, LIGHTS_COL_START, "Special 2", curses.A_BOLD)
    stdscr.addstr(LIGHTS_HAZARD_ROW, LIGHTS_COL_START, "Hazard", curses.A_BOLD)

    # stdscr.addstr(LIGHTS_POS_ROW, LIGHTS_A_COL, "-")
    # stdscr.addstr(LIGHTS_LB_ROW, LIGHTS_A_COL, "-")
    # stdscr.addstr(LIGHTS_HB_ROW, LIGHTS_A_COL, "-")
    # stdscr.addstr(LIGHTS_BRAKE_ROW, LIGHTS_A_COL, "-")
    stdscr.addstr(LIGHTS_RTURN_ROW, LIGHTS_A_COL, "-")
    stdscr.addstr(LIGHTS_LTURN_ROW, LIGHTS_A_COL, "-")
    # stdscr.addstr(LIGHTS_REV_ROW, LIGHTS_A_COL, "-")
    # stdscr.addstr(LIGHTS_FOG_ROW, LIGHTS_A_COL, "-")
    # stdscr.addstr(LIGHTS_INT_ROW, LIGHTS_A_COL, "-")
    # stdscr.addstr(LIGHTS_SPECIAL1_ROW, LIGHTS_A_COL, "-")
    # stdscr.addstr(LIGHTS_SPECIAL2_ROW, LIGHTS_A_COL, "-")
    stdscr.addstr(LIGHTS_HAZARD_ROW, LIGHTS_A_COL, "-")

    stdscr.addstr(LIGHTS_POS_ROW, LIGHTS_R_COL, "-")
    stdscr.addstr(LIGHTS_LB_ROW, LIGHTS_R_COL, "-")
    stdscr.addstr(LIGHTS_HB_ROW, LIGHTS_R_COL, "-")
    stdscr.addstr(LIGHTS_BRAKE_ROW, LIGHTS_R_COL, "-")
    stdscr.addstr(LIGHTS_RTURN_ROW, LIGHTS_R_COL, "-")
    stdscr.addstr(LIGHTS_LTURN_ROW, LIGHTS_R_COL, "-")
    stdscr.addstr(LIGHTS_REV_ROW, LIGHTS_R_COL, "-")
    stdscr.addstr(LIGHTS_FOG_ROW, LIGHTS_R_COL, "-")
    stdscr.addstr(LIGHTS_INT_ROW, LIGHTS_R_COL, "-")
    stdscr.addstr(LIGHTS_SPECIAL1_ROW, LIGHTS_R_COL, "-")
    stdscr.addstr(LIGHTS_SPECIAL2_ROW, LIGHTS_R_COL, "-")
    stdscr.addstr(LIGHTS_HAZARD_ROW, LIGHTS_R_COL, "-")

    stdscr.addstr(LIGHTS_POS_ROW, LIGHTS_S_COL, "-")
    stdscr.addstr(LIGHTS_LB_ROW, LIGHTS_S_COL, "-")
    stdscr.addstr(LIGHTS_HB_ROW, LIGHTS_S_COL, "-")
    stdscr.addstr(LIGHTS_BRAKE_ROW, LIGHTS_S_COL, "-")
    stdscr.addstr(LIGHTS_RTURN_ROW, LIGHTS_S_COL, "-")
    stdscr.addstr(LIGHTS_LTURN_ROW, LIGHTS_S_COL, "-")
    stdscr.addstr(LIGHTS_REV_ROW, LIGHTS_S_COL, "-")
    stdscr.addstr(LIGHTS_FOG_ROW, LIGHTS_S_COL, "-")
    stdscr.addstr(LIGHTS_INT_ROW, LIGHTS_S_COL, "-")
    stdscr.addstr(LIGHTS_SPECIAL1_ROW, LIGHTS_S_COL, "-")
    stdscr.addstr(LIGHTS_SPECIAL2_ROW, LIGHTS_S_COL, "-")
    stdscr.addstr(LIGHTS_HAZARD_ROW, LIGHTS_S_COL, "-")

    stdscr.addstr(LIGHTS_POS_ROW, LIGHTS_C_COL, "-")
    stdscr.addstr(LIGHTS_LB_ROW, LIGHTS_C_COL, "-")
    stdscr.addstr(LIGHTS_HB_ROW, LIGHTS_C_COL, "-")
    stdscr.addstr(LIGHTS_BRAKE_ROW, LIGHTS_C_COL, "-")
    stdscr.addstr(LIGHTS_RTURN_ROW, LIGHTS_C_COL, "-")
    stdscr.addstr(LIGHTS_LTURN_ROW, LIGHTS_C_COL, "-")
    stdscr.addstr(LIGHTS_REV_ROW, LIGHTS_C_COL, "-")
    stdscr.addstr(LIGHTS_FOG_ROW, LIGHTS_C_COL, "-")
    stdscr.addstr(LIGHTS_INT_ROW, LIGHTS_C_COL, "-")
    stdscr.addstr(LIGHTS_SPECIAL1_ROW, LIGHTS_C_COL, "-")
    stdscr.addstr(LIGHTS_SPECIAL2_ROW, LIGHTS_C_COL, "-")
    # stdscr.addstr(LIGHTS_HAZARD_ROW, LIGHTS_C_COL, "-")

    # Steer
    stdscr.addstr(STEER_ROW_START, STEER_A_COL, "A", curses.A_BOLD)
    stdscr.addstr(STEER_ROW_START, STEER_R_COL, "R", curses.A_BOLD)
    stdscr.addstr(STEER_ROW_START, STEER_S_COL, "S", curses.A_BOLD)
    stdscr.addstr(STEER_ROW_START, STEER_C_COL, "C", curses.A_BOLD)
    stdscr.addstr(STEER_DATA_ROW, STEER_COL_START, "Steer", curses.A_BOLD)

    stdscr.addstr(STEER_DATA_ROW, SPEED_A_COL, "-")
    stdscr.addstr(STEER_DATA_ROW, SPEED_R_COL, "-")
    stdscr.addstr(STEER_DATA_ROW, SPEED_S_COL, "-")
    stdscr.addstr(STEER_DATA_ROW, STEER_C_COL, "-")

    # Speed
    stdscr.addstr(SPEED_ROW_START, SPEED_A_COL, "A", curses.A_BOLD)
    stdscr.addstr(SPEED_ROW_START, SPEED_R_COL, "R", curses.A_BOLD)
    stdscr.addstr(SPEED_ROW_START, SPEED_S_COL, "S", curses.A_BOLD)
    stdscr.addstr(SPEED_ROW_START, SPEED_C_COL, "C", curses.A_BOLD)
    stdscr.addstr(SPEED_DATA_ROW, SPEED_COL_START, "Speed", curses.A_BOLD)

    stdscr.addstr(SPEED_DATA_ROW, SPEED_A_COL, "-")
    stdscr.addstr(SPEED_DATA_ROW, SPEED_R_COL, "-")
    stdscr.addstr(SPEED_DATA_ROW, SPEED_S_COL, "-")
    stdscr.addstr(SPEED_DATA_ROW, SPEED_C_COL, "-")

    stdscr.refresh()

def get_agent_actor(world, role_name):
        actors = world.get_actors().filter('*vehicle*')
        for car in actors:
            if car.attributes['role_name'] == role_name:
                return car
        return None

def dataLoop(stdscr):
    global ego_vehicle

    while(is_running):
        ego_vehicle = get_agent_actor(carla_world, "heroAW")
        # Output lights
        if ego_vehicle is not None and ego_vehicle.is_alive:
            try:
                vehicle_lights = ego_vehicle.get_light_state()

                stdscr.addstr(LIGHTS_POS_ROW, LIGHTS_C_COL, "1" if vehicle_lights & carla.VehicleLightState.Position else "0")
                stdscr.addstr(LIGHTS_LB_ROW, LIGHTS_C_COL, "1" if vehicle_lights & carla.VehicleLightState.LowBeam else "0")
                stdscr.addstr(LIGHTS_HB_ROW, LIGHTS_C_COL, "1" if vehicle_lights & carla.VehicleLightState.HighBeam else "0")
                stdscr.addstr(LIGHTS_BRAKE_ROW, LIGHTS_C_COL, "1" if vehicle_lights & carla.VehicleLightState.Brake else "0")
                stdscr.addstr(LIGHTS_RTURN_ROW, LIGHTS_C_COL, "1" if vehicle_lights & carla.VehicleLightState.RightBlinker else "0")
                stdscr.addstr(LIGHTS_LTURN_ROW, LIGHTS_C_COL, "1" if vehicle_lights & carla.VehicleLightState.LeftBlinker else "0")
                stdscr.addstr(LIGHTS_REV_ROW, LIGHTS_C_COL, "1" if vehicle_lights & carla.VehicleLightState.Reverse else "0")
                stdscr.addstr(LIGHTS_FOG_ROW, LIGHTS_C_COL, "1" if vehicle_lights & carla.VehicleLightState.Fog else "0")
                stdscr.addstr(LIGHTS_INT_ROW, LIGHTS_C_COL, "1" if vehicle_lights & carla.VehicleLightState.Interior else "0")
                stdscr.addstr(LIGHTS_SPECIAL1_ROW, LIGHTS_C_COL, "1" if vehicle_lights & carla.VehicleLightState.Special1 else "0")
                stdscr.addstr(LIGHTS_SPECIAL2_ROW, LIGHTS_C_COL, "1" if vehicle_lights & carla.VehicleLightState.Special2 else "0")

                # if (vehicle_lights & carla.VehicleLightState.RightBlinker and vehicle_lights & carla.VehicleLightState.LeftBlinker):
                #     stdscr.addstr(LIGHTS_HAZARD_ROW, LIGHTS_C_COL, "1")
                #     stdscr.addstr(LIGHTS_RTURN_ROW, LIGHTS_C_COL, "0")
                #     stdscr.addstr(LIGHTS_LTURN_ROW, LIGHTS_C_COL, "0")
                # else:
                #     stdscr.addstr(LIGHTS_HAZARD_ROW, LIGHTS_C_COL, "0")


                # Steering
                stdscr.addstr(STEER_DATA_ROW, STEER_C_COL, "%.2f" % ego_vehicle.get_wheel_steer_angle(carla.VehicleWheelLocation.Front_Wheel))

                # Speed
                stdscr.addstr(SPEED_DATA_ROW, SPEED_C_COL, "%.2f" % (ego_vehicle.get_velocity().length() * 3.6))
            except:
                pass
        else:
            # ego_vehicle = get_agent_actor(carla_world, "heroAW")

            stdscr.chgat(LIGHTS_POS_ROW, LIGHTS_C_COL, 1, curses.A_DIM)
            stdscr.chgat(LIGHTS_LB_ROW, LIGHTS_C_COL, 1, curses.A_DIM)
            stdscr.chgat(LIGHTS_HB_ROW, LIGHTS_C_COL, 1, curses.A_DIM)
            stdscr.chgat(LIGHTS_BRAKE_ROW, LIGHTS_C_COL, 1, curses.A_DIM)
            stdscr.chgat(LIGHTS_RTURN_ROW, LIGHTS_C_COL, 1, curses.A_DIM)
            stdscr.chgat(LIGHTS_LTURN_ROW, LIGHTS_C_COL, 1, curses.A_DIM)
            stdscr.chgat(LIGHTS_REV_ROW, LIGHTS_C_COL, 1, curses.A_DIM)
            stdscr.chgat(LIGHTS_FOG_ROW, LIGHTS_C_COL, 1, curses.A_DIM)
            stdscr.chgat(LIGHTS_INT_ROW, LIGHTS_C_COL, 1, curses.A_DIM)
            stdscr.chgat(LIGHTS_SPECIAL1_ROW, LIGHTS_C_COL, 1, curses.A_DIM)
            stdscr.chgat(LIGHTS_SPECIAL2_ROW, LIGHTS_C_COL, 1, curses.A_DIM)

            stdscr.chgat(STEER_DATA_ROW, STEER_C_COL, 1, curses.A_DIM)
            stdscr.chgat(SPEED_DATA_ROW, SPEED_C_COL, 1, curses.A_DIM)

        stdscr.refresh()

        time.sleep(0.1)

    stdscr.clear()

def sig_handler(signum, frame):
    global is_running
    is_running = False

def on_turn_status(data):
    if data.report == TurnIndicatorsReport.ENABLE_RIGHT:
        stdscr_g.addstr(LIGHTS_RTURN_ROW, LIGHTS_S_COL, "1")
        stdscr_g.addstr(LIGHTS_LTURN_ROW, LIGHTS_S_COL, "0")
    elif data.report == TurnIndicatorsReport.ENABLE_LEFT:
        stdscr_g.addstr(LIGHTS_RTURN_ROW, LIGHTS_S_COL, "0")
        stdscr_g.addstr(LIGHTS_LTURN_ROW, LIGHTS_S_COL, "1")
    elif data.report == TurnIndicatorsReport.DISABLE:
        stdscr_g.addstr(LIGHTS_RTURN_ROW, LIGHTS_S_COL, "0")
        stdscr_g.addstr(LIGHTS_LTURN_ROW, LIGHTS_S_COL, "0")
    else:
        stdscr_g.addstr(LIGHTS_RTURN_ROW, LIGHTS_S_COL, "-")
        stdscr_g.addstr(LIGHTS_LTURN_ROW, LIGHTS_S_COL, "-")

def on_turn_requested(data):
    global on_turn_requested_previous
    if data.command == TurnIndicatorsCommand.ENABLE_RIGHT:
        stdscr_g.addstr(LIGHTS_RTURN_ROW, LIGHTS_A_COL, "1")
        stdscr_g.addstr(LIGHTS_LTURN_ROW, LIGHTS_A_COL, "0")
    elif data.command == TurnIndicatorsCommand.ENABLE_LEFT:
        stdscr_g.addstr(LIGHTS_RTURN_ROW, LIGHTS_A_COL, "0")
        stdscr_g.addstr(LIGHTS_LTURN_ROW, LIGHTS_A_COL, "1")
        on_turn_requested_previous = data
        stdscr_g.addstr(LIGHTS_RTURN_ROW, LIGHTS_A_COL, "0")
        stdscr_g.addstr(LIGHTS_LTURN_ROW, LIGHTS_A_COL, "0")
    elif data.command == TurnIndicatorsCommand.NO_COMMAND:
        stdscr_g.chgat(LIGHTS_RTURN_ROW, LIGHTS_A_COL, 1, curses.A_DIM)
        stdscr_g.chgat(LIGHTS_LTURN_ROW, LIGHTS_A_COL, 1, curses.A_DIM)
    else:
        stdscr_g.addstr(LIGHTS_RTURN_ROW, LIGHTS_A_COL, "-")
        stdscr_g.addstr(LIGHTS_LTURN_ROW, LIGHTS_A_COL, "-") 

def on_hazard_status(data):
    if data.report == HazardLightsReport.ENABLE:
        stdscr_g.addstr(LIGHTS_HAZARD_ROW, LIGHTS_S_COL, "1")
    elif data.report == HazardLightsReport.DISABLE:
        stdscr_g.addstr(LIGHTS_HAZARD_ROW, LIGHTS_S_COL, "0")
    else:
        stdscr_g.addstr(LIGHTS_HAZARD_ROW, LIGHTS_S_COL, "-")

def on_hazard_requested(data):
    if data.command == HazardLightsCommand.ENABLE:
        stdscr_g.addstr(LIGHTS_HAZARD_ROW, LIGHTS_A_COL, "1")
    elif data.command == HazardLightsCommand.DISABLE:
        stdscr_g.addstr(LIGHTS_HAZARD_ROW, LIGHTS_A_COL, "0")
    elif data.command == HazardLightsCommand.NO_COMMAND:
        stdscr_g.chgat(LIGHTS_HAZARD_ROW, LIGHTS_A_COL, 1, curses.A_DIM)
    else:
        stdscr_g.addstr(LIGHTS_HAZARD_ROW, LIGHTS_A_COL, "-")

def on_speed_status(data):
    stdscr_g.addstr(SPEED_DATA_ROW, SPEED_S_COL, "%.2f" % (data.longitudinal_velocity * 3.6))

def on_steer_status(data):
    stdscr_g.addstr(STEER_DATA_ROW, SPEED_S_COL, "%.2f" % math.degrees(data.steering_tire_angle))

def on_carla_ackermann_cmd(data):
    stdscr_g.addstr(SPEED_DATA_ROW, SPEED_R_COL, "%.2f" % (data.speed * 3.6))
    stdscr_g.addstr(STEER_DATA_ROW, SPEED_R_COL, "%.2f" % math.degrees(data.steering_angle))

def on_autoware_ackermann_cmd(data):
    stdscr_g.addstr(SPEED_DATA_ROW, SPEED_A_COL, "%.2f" % (data.longitudinal.speed * 3.6))
    stdscr_g.addstr(STEER_DATA_ROW, SPEED_A_COL, "%.2f" % math.degrees(data.lateral.steering_tire_angle))

def on_carla_lights_cmd(data):
    stdscr_g.chgat(LIGHTS_POS_ROW, LIGHTS_R_COL, 1, curses.A_DIM)
    stdscr_g.chgat(LIGHTS_LB_ROW, LIGHTS_R_COL, 1, curses.A_DIM)
    stdscr_g.chgat(LIGHTS_HB_ROW, LIGHTS_R_COL, 1, curses.A_DIM)
    stdscr_g.chgat(LIGHTS_BRAKE_ROW, LIGHTS_R_COL, 1, curses.A_DIM)
    stdscr_g.chgat(LIGHTS_RTURN_ROW, LIGHTS_R_COL, 1, curses.A_DIM)
    stdscr_g.chgat(LIGHTS_LTURN_ROW, LIGHTS_R_COL, 1, curses.A_DIM)
    stdscr_g.chgat(LIGHTS_REV_ROW, LIGHTS_R_COL, 1, curses.A_DIM)
    stdscr_g.chgat(LIGHTS_FOG_ROW, LIGHTS_R_COL, 1, curses.A_DIM)
    stdscr_g.chgat(LIGHTS_INT_ROW, LIGHTS_R_COL, 1, curses.A_DIM)
    stdscr_g.chgat(LIGHTS_SPECIAL1_ROW, LIGHTS_R_COL, 1, curses.A_DIM)
    stdscr_g.chgat(LIGHTS_SPECIAL2_ROW, LIGHTS_R_COL, 1, curses.A_DIM)
    stdscr_g.chgat(LIGHTS_HAZARD_ROW, LIGHTS_R_COL, 1, curses.A_DIM)

    if data.position is not CarlaEgoVehicleLight.NO_COMMAND:
        if data.position is CarlaEgoVehicleLight.ON:
            stdscr_g.addstr(LIGHTS_POS_ROW, LIGHTS_R_COL, "1")
        elif data.position is CarlaEgoVehicleLight.OFF:
            stdscr_g.addstr(LIGHTS_POS_ROW, LIGHTS_R_COL, "0")
    if data.low_beam is not CarlaEgoVehicleLight.NO_COMMAND:
        if data.low_beam is CarlaEgoVehicleLight.ON:
            stdscr_g.addstr(LIGHTS_LB_ROW, LIGHTS_R_COL, "1")
        elif data.low_beam is CarlaEgoVehicleLight.OFF:
            stdscr_g.addstr(LIGHTS_LB_ROW, LIGHTS_R_COL, "0")
    if data.high_beam is not CarlaEgoVehicleLight.NO_COMMAND:
        if data.high_beam is CarlaEgoVehicleLight.ON:
            stdscr_g.addstr(LIGHTS_HB_ROW, LIGHTS_R_COL, "1")
        elif data.high_beam is CarlaEgoVehicleLight.OFF:
            stdscr_g.addstr(LIGHTS_HB_ROW, LIGHTS_R_COL, "0")
    if data.brake is not CarlaEgoVehicleLight.NO_COMMAND:
        if data.brake is CarlaEgoVehicleLight.ON:
            stdscr_g.addstr(LIGHTS_BRAKE_ROW, LIGHTS_R_COL, "1")
        elif data.brake is CarlaEgoVehicleLight.OFF:
            stdscr_g.addstr(LIGHTS_BRAKE_ROW, LIGHTS_R_COL, "0")
    if data.right_blinker is not CarlaEgoVehicleLight.NO_COMMAND:
        if data.right_blinker is CarlaEgoVehicleLight.ON:
            stdscr_g.addstr(LIGHTS_RTURN_ROW, LIGHTS_R_COL, "1")
        elif data.right_blinker is CarlaEgoVehicleLight.OFF:
            stdscr_g.addstr(LIGHTS_RTURN_ROW, LIGHTS_R_COL, "0")
    if data.left_blinker is not CarlaEgoVehicleLight.NO_COMMAND:
        if data.left_blinker is CarlaEgoVehicleLight.ON:
            stdscr_g.addstr(LIGHTS_LTURN_ROW, LIGHTS_R_COL, "1")
        elif data.left_blinker is CarlaEgoVehicleLight.OFF:
            stdscr_g.addstr(LIGHTS_LTURN_ROW, LIGHTS_R_COL, "0")
    if data.reverse is not CarlaEgoVehicleLight.NO_COMMAND:
        if data.reverse is CarlaEgoVehicleLight.ON:
            stdscr_g.addstr(LIGHTS_REV_ROW, LIGHTS_R_COL, "1")
        elif data.reverse is CarlaEgoVehicleLight.OFF:
            stdscr_g.addstr(LIGHTS_REV_ROW, LIGHTS_R_COL, "0")
    if data.fog is not CarlaEgoVehicleLight.NO_COMMAND:
        if data.fog is CarlaEgoVehicleLight.ON:
            stdscr_g.addstr(LIGHTS_FOG_ROW, LIGHTS_R_COL, "1")
        elif data.fog is CarlaEgoVehicleLight.OFF:
            stdscr_g.addstr(LIGHTS_FOG_ROW, LIGHTS_R_COL, "0")
    if data.interior is not CarlaEgoVehicleLight.NO_COMMAND:
        if data.interior is CarlaEgoVehicleLight.ON:
            stdscr_g.addstr(LIGHTS_INT_ROW, LIGHTS_R_COL, "1")
        elif data.interior is CarlaEgoVehicleLight.OFF:
            stdscr_g.addstr(LIGHTS_INT_ROW, LIGHTS_R_COL, "0")
    if data.special1 is not CarlaEgoVehicleLight.NO_COMMAND:
        if data.special1 is CarlaEgoVehicleLight.ON:
            stdscr_g.addstr(LIGHTS_SPECIAL1_ROW, LIGHTS_R_COL, "1")
        elif data.special1 is CarlaEgoVehicleLight.OFF:
            stdscr_g.addstr(LIGHTS_SPECIAL1_ROW, LIGHTS_R_COL, "0")
    if data.special2 is not CarlaEgoVehicleLight.NO_COMMAND:
        if data.special2 is CarlaEgoVehicleLight.ON:
            stdscr_g.addstr(LIGHTS_SPECIAL1_ROW, LIGHTS_R_COL, "1")
        elif data.special2 is CarlaEgoVehicleLight.OFF:
            stdscr_g.addstr(LIGHTS_SPECIAL1_ROW, LIGHTS_R_COL, "0")
    if data.hazard is not CarlaEgoVehicleLight.NO_COMMAND:
        if data.hazard is CarlaEgoVehicleLight.ON:
            stdscr_g.addstr(LIGHTS_HAZARD_ROW, LIGHTS_R_COL, "1")
        elif data.hazard is CarlaEgoVehicleLight.OFF:
            stdscr_g.addstr(LIGHTS_HAZARD_ROW, LIGHTS_R_COL, "0")

parser = argparse.ArgumentParser(description="Ros Carla Bridge debug", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument_group()
parser.add_argument("--host", help="Carla host", default="172.29.144.1")
parser.add_argument("--port", help="Carla Port", default=2000)
parser.add_argument("--no-carla", action="store_true", help="Disable Carla connection")
parser.add_argument("--no-ros", action="store_true", help="Disable ROS2 Topic connections")

args = parser.parse_args()
config = vars(args)
print(config)

signal.signal(signal.SIGINT, sig_handler)

carla_client = carla.Client(
            host=config['host'],
            port=config['port'])
carla_client.set_timeout(20)
carla_world = carla_client.get_world()
ego_vehicle = get_agent_actor(carla_world, "heroAW")

rclpy.init(args=None)
ros2_node = rclpy.create_node("op_ros2_agent")
# ros2_executor = MultiThreadedExecutor()
# ros2_callback_group = ReentrantCallbackGroup()

turn_requested_sub = ros2_node.create_subscription(TurnIndicatorsCommand, "/control/command/turn_indicators_cmd", on_turn_requested, 1)
hazard_requested_sub = ros2_node.create_subscription(HazardLightsCommand, "/control/command/hazard_lights_cmd", on_hazard_requested, 1)
turn_status_sub = ros2_node.create_subscription(TurnIndicatorsReport, "/vehicle/status/turn_indicators_status", on_turn_status, 1)
hazard_status_sub = ros2_node.create_subscription(HazardLightsReport, "/vehicle/status/hazard_lights_status", on_hazard_status, 1)
carla_lights_sub = ros2_node.create_subscription(CarlaEgoVehicleLight, "/carla/heroAW/vehicle_light_cmd", on_carla_lights_cmd, 1)
speed_status_sub = ros2_node.create_subscription(VelocityReport, "/vehicle/status/velocity_status", on_speed_status, 1)
steer_status_sub = ros2_node.create_subscription(SteeringReport, "/vehicle/status/steering_status", on_steer_status, 1)
carla_ackermann_sub = ros2_node.create_subscription(AckermannDrive, "/carla/heroAW/ackermann_cmd", on_carla_ackermann_cmd, 1)
autoware_ackermann_sub = ros2_node.create_subscription(AckermannControlCommand, "/control/command/control_cmd", on_autoware_ackermann_cmd, 1)



spin_thread = threading.Thread(target=rclpy.spin, args=(ros2_node,))
spin_thread.start()

curses.wrapper(main)