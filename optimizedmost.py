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

# map for the tiles

visited_tiles = [[0 for _ in range(8)] for _ in range(8)]

OUTOFBOUND = 2000
MAXSTEPS = 1000

WALLSINIT = 0
WALLSOPEN = 1
WALLSBLOCKED = 2

# --- indices for tile wall directions
NORTHIND = 0
EASTIND = 1
SOUTHIND = 2
WESTIND = 3

# initialize all walls to WALLSINIT value
tile_walls = [
    [[0] * 4,[0] * 4,[0] * 4,[0] * 4,[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
    [[0 for _ in range(4)] for _ in range(8)],
    [[0 for _ in range(4)] for _ in range(8)],
    [[0 for _ in range(4)] for _ in range(8)],
    [[0 for _ in range(4)] for _ in range(8)],
    [[0 for _ in range(4)] for _ in range(8)],
    [[0 for _ in range(4)] for _ in range(8)],
    [[0 for _ in range(4)] for _ in range(8)],
]
# ----- end of not used yet


heading = 0
rotation = 0
xpos = location.position(X,MM)
ypos = location.position(Y,MM)
numRow = OUTOFBOUND
numCol = OUTOFBOUND

tile_dist = 250
tile_center = tile_dist / 2

# Function convert x to column
def XtoColumn():
    global numCol
    x = location.position(X,MM)
    numCol = round ((x - tile_center) / tile_dist) + 4
        
    return numCol

# Function to conver y to row
def YtoRow():
    global numRow
    y = location.position(Y,MM)

    # Zero row start at top so flip the axis
    y = y * -1
    numRow = round ((y - tile_center) / tile_dist) + 4
  
    return numRow

# Function mark starting tile
def marktile(row, col, visited):
    global visted_tiles, xpos, ypos
    
    visited_tiles[row][col] = visited_tiles[row][col] + visited
    xpos = location.position(X,MM)
    ypos = location.position(Y,MM)

def rotate_to_best_dir():
        global OUTOFBOUND
        global WALLSINIT, WALLSOPEN, WALLSBLOCKED
        global NORTHIND, EASTIND, SOUTHIND, WESTIND
        global tile_walls

        #check if already been to next tile
        numRow = YtoRow()
        numCol = XtoColumn()

        # check for out of bounds
        if (numRow > 0):
            northcount = visited_tiles[numRow-1][numCol]
        else:
            northcount = OUTOFBOUND
        if (numCol < 7):
            eastcount = visited_tiles[numRow][numCol+1]
        else:
            eastcount = OUTOFBOUND
        if (numRow < 7):
            southcount = visited_tiles[numRow+1][numCol]
        else:
            southcount = OUTOFBOUND
        if (numCol > 0):
            westcount = visited_tiles[numRow][numCol-1]
        else:
            westcount = OUTOFBOUND

        numVisits = 0

        #initialize to unblocked if not initialized
        northblocked = tile_walls[numRow][numCol][NORTHIND]
        eastblocked = tile_walls[numRow][numCol][EASTIND]
        southblocked = tile_walls[numRow][numCol][SOUTHIND]
        westblocked = tile_walls[numRow][numCol][WESTIND]

        if (northblocked == WALLSINIT):
            northblocked = WALLSOPEN
            eastblocked = WALLSOPEN
            southblocked = WALLSOPEN
            westblocked = WALLSOPEN

            # check for blocked walls
            drivetrain.turn_to_heading(0, DEGREES)
            if (front_distance.get_distance(MM) < 100):
                northblocked = WALLSBLOCKED

            drivetrain.turn_to_heading(90, DEGREES)
            if (front_distance.get_distance(MM) < 100):
                eastblocked = WALLSBLOCKED

            drivetrain.turn_to_heading(180, DEGREES)
            if (front_distance.get_distance(MM) < 100):
                southblocked = WALLSBLOCKED

            drivetrain.turn_to_heading(270, DEGREES)
            if (front_distance.get_distance(MM) < 100):
                westblocked = WALLSBLOCKED
                    
            # store changed values back
            tile_walls[numRow][numCol][NORTHIND] = northblocked
            tile_walls[numRow][numCol][EASTIND] = eastblocked
            tile_walls[numRow][numCol][SOUTHIND] = southblocked
            tile_walls[numRow][numCol][WESTIND] = westblocked

        # find the open direct least visited
        while (1):
            # if north is not border or closed 
            if ((not(northcount == OUTOFBOUND)) and (not(northblocked == WALLSBLOCKED))):
                if (northcount == numVisits):
                    drivetrain.turn_to_heading(0, DEGREES)
                    return

            # if east is not border or closed 
            if (not(eastcount == OUTOFBOUND) and (not(eastblocked == WALLSBLOCKED))):
                if (eastcount == numVisits):
                    drivetrain.turn_to_heading(90, DEGREES)
                    return

            # if south is border skip
            if (not(southcount == OUTOFBOUND) and (not(southblocked == WALLSBLOCKED))):
                if (southcount == numVisits):
                    drivetrain.turn_to_heading(180, DEGREES)
                    return

            # if west is border skip
            if (not(westcount == OUTOFBOUND) and (not(westblocked == WALLSBLOCKED))):
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
    global MAXSTEPS

    heading = drivetrain.heading(DEGREES)
    rotation = drivetrain.rotation(DEGREES)

    monitor_variable("visited_tiles")
    monitor_variable("tile_walls")
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
    # solve in MAXSTEPS
    while (i < MAXSTEPS): 
        wait(5, MSEC)
        i = i+1

        #find least visited direction
        rotate_to_best_dir()
        drive_safe(FORWARD, tile_dist, MM)
        if (down_eye.detect(RED)):
            break

# VR threads — Do not delete
vr_thread(main)
