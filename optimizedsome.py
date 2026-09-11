#region VEXcode Generated Robot Configuration
import math
import random
from vexcode_vr import *

# Brain should be defined by default
brain=Brain()

drivetrain = Drivetrain("drivetrain", 0)
pen = Pen("pen", 8)
pen.set_pen_width(THIN)
left_bumper = Bumper("leftBumper", 2)
right_bumper = Bumper("rightBumper", 3)
front_eye = EyeSensor("frontEye", 4)
down_eye = EyeSensor("downEye", 5)
front_distance = Distance("frontdistance", 6)
distance = front_distance
magnet = Electromagnet("magnet", 7)
location = Location("location", 9)

#endregion VEXcode Generated Robot Configuration
# ------------------------------------------
# 
# 	Project:      VEXcode Project
#	Author:       VEX
#	Created:
#	Description:  VEXcode VR Python Project
# 
# ------------------------------------------

visited_tiles = [
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0]
]

# --- not used yet
NORTHIND = 0
EASTIND = 1
SOUTHIND = 2
WESTIND = 3

tile_walls = [
    [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
    [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
    [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
    [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
    [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
    [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
    [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
    [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
]
# ----- end of not used yet

tile_dist = 255
heading = 0
rotation = 0
xpos = location.position(X,MM)
ypos = location.position(Y,MM)
numRow = 100
numCol = 200

# Function convert x to column
def XtoColumn():
    global numCol
    x = location.position(X,MM)

    if ((x > -960) and (x < -860)):
        numCol = 0
    if ((x > -700) and (x < -600)):
        numCol = 1
    if ((x > -440) and (x < -340)):
        numCol = 2
    if ((x > -180) and (x < -80)):
        numCol = 3
    if ((x < 960) and (x > 860)):
        numCol = 7
    if ((x < 700) and (x > 600)):
        numCol = 6
    if ((x < 440) and (x > 340)):
        numCol = 5
    if ((x < 180) and (x > 80)):
        numCol = 4
        
    return numCol

# Function to conver y to row
def YtoRow():
    global numRow
    y = location.position(Y,MM)

    if ((y > -960) and (y < -860)):
        numRow = 7
    if ((y > -700) and (y < -600)):
        numRow = 6
    if ((y > -440) and (y < -340)):
        numRow = 5
    if ((y > -180) and (y < -80)):
        numRow = 4
    if ((y < 960) and (y > 860)):
        numRow = 0
    if ((y < 700) and (y > 600)):
        numRow = 1
    if ((y < 440) and (y > 340)):
        numRow = 2
    if ((y < 180) and (y > 80)):
        numRow = 3
  
    return numRow

# Function mark starting tile
def marktile(row, col, visited):
    global visted_tiles, xpos, ypos
    
    visited_tiles[row][col] = visited_tiles[row][col] + visited
    xpos = location.position(X,MM)
    ypos = location.position(Y,MM)

def rotate_to_best_dir():
        #check if already been to next tile
        numRow = YtoRow()
        numCol = XtoColumn()

        # check for out of bounds
        if (numRow > 0):
            northcount = visited_tiles[numRow-1][numCol]
        else:
            northcount = 1000
        if (numCol < 7):
            eastcount = visited_tiles[numRow][numCol+1]
        else:
            eastcount = 1000
        if (numRow < 7):
            southcount = visited_tiles[numRow+1][numCol]
        else:
            southcount = 1000
        if (numCol > 0):
            westcount = visited_tiles[numRow][numCol-1]
        else:
            westcount = 1000

        numVisits = 0

        #initialize to unblocked
        northblocked = 0
        eastblocked = 0
        southblocked = 0
        westblocked = 0

        # check for blocked walls
        drivetrain.turn_to_heading(0, DEGREES)
        if (front_distance.get_distance(MM) < 100):
            northblocked = 1

        drivetrain.turn_to_heading(90, DEGREES)
        if (front_distance.get_distance(MM) < 100):
            eastblocked = 1

        drivetrain.turn_to_heading(180, DEGREES)
        if (front_distance.get_distance(MM) < 100):
            southblocked = 1

        drivetrain.turn_to_heading(270, DEGREES)
        if (front_distance.get_distance(MM) < 100):
            westblocked = 1
                  
        # find the open direct least visited
        while (1):
            # if north is not border or closed 
            if ((not(northcount == 1000)) and (northblocked == 0)):
                if (northcount == numVisits):
                    drivetrain.turn_to_heading(0, DEGREES)
                    return

            # if east is not border or closed 
            if (not(eastcount == 1000) and (eastblocked == 0)):
                if (eastcount == numVisits):
                    drivetrain.turn_to_heading(90, DEGREES)
                    return

            # if east is border skip
            if (not(southcount == 1000) and (southblocked == 0)):
                if (southcount == numVisits):
                    drivetrain.turn_to_heading(180, DEGREES)
                    return

            # if east is border skip
            if (not(westcount == 1000) and (westblocked == 0)):
                if (westcount == numVisits):
                    drivetrain.turn_to_heading(270, DEGREES)
                    return

            numVisits = numVisits + 1
            wait(5, MSEC)
         

def drive_safe(direction, drivedist, unit):
    global ypos
    ysouthborder = -940
    ynorthborder = 940

    ypos = location.position(Y,MM)
        
    if ((ypos < ysouthborder) and (drivetrain.heading(DEGREES) == 180)):
        drivetrain.turn_for(RIGHT, 90, DEGREES)
    else:
        if (ypos > ynorthborder):
            drivetrain.turn_to_heading(0, DEGREES)

        drivetrain.drive_for(direction, drivedist, unit)
        numRow = YtoRow()
        numCol = XtoColumn()
        marktile(numRow, numCol, 1)


# Add project code in "main"
def main():
    global visited_tiles, tile_dist
    global heading, rotation
    global xpos, ypos, numRow, numCol

    heading = drivetrain.heading(DEGREES)
    rotation = drivetrain.rotation(DEGREES)

    monitor_variable("visited_tiles")
    monitor_variable("tile_dist")
    monitor_variable("heading")
    monitor_variable("rotation")
    monitor_variable("xpos")
    monitor_variable("ypos")
    monitor_variable("numRow")
    monitor_variable("numCol")

    #drivetrain mark starting tile
    xpos = location.position(X,MM)
    ypos = location.position(Y,MM)
    
    numRow = YtoRow()
    numCol = XtoColumn()
    marktile(numRow, numCol, 1)

    i = 0
    while (i < 1000): 
        wait(5, MSEC)
        i = i+1

        while (front_distance.get_distance(MM) < 100):
            drivetrain.turn_for(RIGHT, 90, DEGREES)

        #find best direction
        rotate_to_best_dir()
        drive_safe(FORWARD, tile_dist, MM)
        if (down_eye.detect(RED)):
            break

# VR threads — Do not delete
vr_thread(main)