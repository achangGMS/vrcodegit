#region VEXcode Generated Robot Configuration
import math
import random
from vexcode_vr import *

# Brain should be defined by default
brain=Brain()

drivetrain = Drivetrain("drivetrain", 0)
rover = Rover("ai", 1)
distance = Distance("distance", 6)

#endregion VEXcode Generated Robot Configuration
# ------------------------------------------
# 
# 	Project:      VEXcode Project
#	Author:       VEX
#	Created:
#	Description:  VEXcode VR Python Project
# 
# ------------------------------------------

# test custom event
def run_on_dance():
    # do a little dance
    for repeat_count in range(2): 
        drivetrain.turn_for(RIGHT, 30, DEGREES)
        wait(500, MSEC)
        drivetrain.turn_for(LEFT, 30, DEGREES)
        wait(500, MSEC)

    brain.print("Yay")
    brain.new_line()

dance_event = Event()

def wiggle_loose():
    oldheading = drivetrain.heading(DEGREES)
    drivetrain.turn_for(LEFT, 15, DEGREES)
    newheading = drivetrain.heading(DEGREES)
    # if stuck
    if (oldheading-2 < newheading < oldheading+2):  
        #stuck turn the other way
        drivetrain.turn_for(RIGHT, 15, DEGREES)
        newheading = drivetrain.heading(DEGREES)
        if (oldheading-2 < newheading < oldheading+2):
            #stuck back up  
            drivetrain.drive_for(REVERSE, 5, MM)

def run_on_under_attack():
    if (rover.sees(MINERALS)):
        if (rover.minerals_stored() < rover.storage_capacity()):
            blocked_dist = min(rover.get_distance(OBSTACLE,MM), rover.get_distance(HAZARD,MM))
            if (rover.get_distance(MINERALS, MM) < blocked_dist):  
                drivetrain.drive_to(MINERALS)
                wait(20, MSEC)
                rover.pickup(MINERALS)

    # run away if rover is low on battery
    if (rover.battery() < 60): 
        if (rover.minerals_stored() > 0):
            rover.drop(MINERALS)
            rover.use(MINERALS)
        wiggle_loose()
        return
    
    while rover.get_distance(ENEMY,MM) < 200:
        attempts = 0
        while ((rover.enemy_radiation() > 0) and (attempts < 300)):
            blocked_dist = min(rover.get_distance(OBSTACLE,MM), rover.get_distance(HAZARD,MM))
            if (rover.get_distance(ENEMY, MM) < blocked_dist):  
                drivetrain.go_to(ENEMY,wait=True)
                rover.absorb_radiation(ENEMY)
                brain.print("enemy radiation is ", rover.enemy_radiation())
                brain.new_line()
                #wait(100, MSEC)
            attempts = attempts + 1
        if (attempts >= 300):
            wiggle_loose()

def slip_proofing():
    x = rover.location(BASE,X,MM)
    y = rover.location(BASE,Y,MM)
    checknum = 0
    while (checknum < 20):
        wait(10, MSEC)
        # has not moved
        if (x-2 < rover.location(BASE,X,MM) < x+2):
            if (y-2 < rover.location(BASE,Y,MM) < y+2):
                checknum = checknum + 1
                x = rover.location(BASE,X,MM)
                y = rover.location(BASE,Y,MM)
            else:  
                return
        else:
            return
    if (checknum >= 20):
        wiggle_loose()

# Add project code in "main"
def main():
    brain.clear()
    drivetrain.set_timeout(2, SECONDS)
    drivetrain.set_drive_velocity(40, PERCENT)
    drivetrain.set_turn_velocity(70, PERCENT)

    # Register callback functions to the events.
    # Wait to allow events to register
    dance_event(run_on_dance)
    wait(15, MSEC)
    rover.on_under_attack(run_on_under_attack)
    wait(15, MSEC)

    while (1):
        checkagain = 0
        hazard_dist = 1000
        blocked_dist = 1000

        # charge if battery low
        if (rover.battery() < 50) and (rover.minerals_stored() > 0):
            rover.drop(MINERALS)
            rover.use(MINERALS)
            dance_event.broadcast_and_wait()

        #slip_proofing()

        if (rover.sees(HAZARD)):
            hazard_dist = rover.get_distance(HAZARD,MM);
        if (rover.sees(OBSTACLE)):
            blocked_dist = rover.get_distance(OBSTACLE,MM);

        if (rover.get_distance(BASE,MM) < 100):
            if (rover.minerals_stored() > 0):
                drivetrain.drive_to(BASE,wait=True)
                rover.drop(MINERALS)

        if ((blocked_dist < 210) or (hazard_dist < 210)):
            drivetrain.drive_for(REVERSE, 5, MM)
            turn_direction = random.randint(1, 3)
            if (turn_direction == 1):
                drivetrain.turn_for(RIGHT, 60, DEGREES)
            else:
                drivetrain.turn_for(LEFT, 60, DEGREES)
            checkagain = checkagain + 1

        if (rover.sees(MINERALS) and (checkagain==0)):
            if (rover.minerals_stored() < rover.storage_capacity()):
                drivetrain.turn_to(MINERALS)   
                blocked_dist = min(rover.get_distance(OBSTACLE,MM), rover.get_distance(HAZARD,MM))
                if (rover.get_distance(MINERALS, MM) < blocked_dist):  
                    drivetrain.drive_to(MINERALS)
                    wait(20, MSEC)
                    rover.pickup(MINERALS)
                else:
                    drivetrain.drive_for(REVERSE, 10, MM)
                    turndegree = random.randint(30, 60)
                    drivetrain.turn_for(RIGHT, turndegree, DEGREES)

        if (checkagain == 0):
            hazard_dist = rover.get_distance(HAZARD,MM)
            blocked_dist = rover.get_distance(OBSTACLE,MM)

            if ((blocked_dist < 210) and (hazard_dist > blocked_dist)):
                wiggle_loose()
                drivetrain.drive_for(FORWARD, min(0, blocked_dist-10), MM)
            else:
                if ((distance.get_distance(MM) >= 210) and (hazard_dist>=210)):
                    drivetrain.drive_for(FORWARD, 200, MM)
                else:
                    drivetrain.drive_for(REVERSE, 10, MM)
                    turndegree = random.randint(45, 120)
                    drivetrain.turn_for(RIGHT, turndegree, DEGREES)

# VR threads — Do not delete
vr_thread(main)

# VR threads — Do not delete
vr_thread(slip_proofing)