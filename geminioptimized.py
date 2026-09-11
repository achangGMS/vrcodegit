#region VEXcode Generated Robot Configuration
import math
import random
from vexcode_vr import *

# Brain should be defined by default
brain = Brain()

# Initialize Drivetrain and attached sensors/actuators
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
# 	Project:     VEXcode Maze Explorer
#	Author:      VEX / Refactored with Comments
#	Description: Autonomous 8x8 Grid Mapping and Maze Exploration
# ------------------------------------------

# 8x8 matrix to track how many times each grid cell/tile has been visited
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

# Direction index constants for referencing wall states
NORTHIND = 0
EASTIND = 1
SOUTHIND = 2
WESTIND = 3

# Wall status flag constants
WALLSINIT = 0      # Unchecked/Uninitialized wall
WALLSOPEN = 1      # Path is open (no wall detected)
WALLSBLOCKED = 2   # Path is blocked by a wall

# 3D structure to track wall states for each of the 8x8 tiles: [row][col][direction]
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

# Navigation settings & tracking variables
tile_dist = 255  # Distance (in mm) between center points of adjacent grid tiles
heading = 0
rotation = 0
xpos = location.position(X, MM)
ypos = location.position(Y, MM)
numRow = 100
numCol = 200

def XtoColumn():
    """Converts the robot's real-time X coordinate (in mm) to an 8x8 grid column index (0-7)."""
    global numCol
    x = location.position(X, MM)

    if (-960 < x < -860):
        numCol = 0
    elif (-700 < x < -600):
        numCol = 1
    elif (-440 < x < -340):
        numCol = 2
    elif (-180 < x < -80):
        numCol = 3
    elif (860 < x < 960):
        numCol = 7
    elif (600 < x < 700):
        numCol = 6
    elif (340 < x < 440):
        numCol = 5
    elif (80 < x < 180):
        numCol = 4
        
    return numCol

def YtoRow():
    """Converts the robot's real-time Y coordinate (in mm) to an 8x8 grid row index (0-7)."""
    global numRow
    y = location.position(Y, MM)

    if (-960 < y < -860):
        numRow = 7
    elif (-700 < y < -600):
        numRow = 6
    elif (-440 < y < -340):
        numRow = 5
    elif (-180 < y < -80):
        numRow = 4
    elif (860 < y > 960):  # Note: mapped from top to bottom
        numRow = 0
    elif (600 < y < 700):
        numRow = 1
    elif (340 < y < 440):
        numRow = 2
    elif (80 < y < 180):
        numRow = 3
  
    return numRow

def marktile(row, col, visited):
    """Increments the visit counter for a specific grid tile and updates stored position coordinates."""
    global visited_tiles, xpos, ypos
    
    visited_tiles[row][col] += visited
    xpos = location.position(X, MM)
    ypos = location.position(Y, MM)

def rotate_to_best_dir():
    """
    Scans surrounding walls (if unmapped) and turns the robot toward the 
    adjacent unblocked tile that has been visited the fewest number of times.
    """
    global WALLSINIT, WALLSOPEN, WALLSBLOCKED
    global NORTHIND, EASTIND, SOUTHIND, WESTIND
    global tile_walls

    numRow = YtoRow()
    numCol = XtoColumn()

    # Get visit counts for neighboring tiles (assign high penalty of 1000 if out of bounds)
    northcount = visited_tiles[numRow-1][numCol] if (numRow > 0) else 1000
    eastcount  = visited_tiles[numRow][numCol+1] if (numCol < 7) else 1000
    southcount = visited_tiles[numRow+1][numCol] if (numRow < 7) else 1000
    westcount  = visited_tiles[numRow][numCol-1] if (numCol > 0) else 1000

    numVisits = 0

    # Retrieve current known wall states for this tile
    northblocked = tile_walls[numRow][numCol][NORTHIND]
    eastblocked  = tile_walls[numRow][numCol][EASTIND]
    southblocked = tile_walls[numRow][numCol][SOUTHIND]
    westblocked  = tile_walls[numRow][numCol][WESTIND]

    # If walls haven't been scanned yet for this tile, rotate 360° to scan all 4 directions
    if (northblocked == WALLSINIT):
        northblocked = WALLSOPEN
        eastblocked  = WALLSOPEN
        southblocked = WALLSOPEN
        westblocked  = WALLSOPEN

        # Scan North (0°)
        drivetrain.turn_to_heading(0, DEGREES)
        if (front_distance.get_distance(MM) < 100):
            northblocked = WALLSBLOCKED

        # Scan East (90°)
        drivetrain.turn_to_heading(90, DEGREES)
        if (front_distance.get_distance(MM) < 100):
            eastblocked = WALLSBLOCKED

        # Scan South (180°)
        drivetrain.turn_to_heading(180, DEGREES)
        if (front_distance.get_distance(MM) < 100):
            southblocked = WALLSBLOCKED

        # Scan West (270°)
        drivetrain.turn_to_heading(270, DEGREES)
        if (front_distance.get_distance(MM) < 100):
            westblocked = WALLSBLOCKED
                
        # Save detected wall states back into the grid memory
        tile_walls[numRow][numCol][NORTHIND] = northblocked
        tile_walls[numRow][numCol][EASTIND]  = eastblocked
        tile_walls[numRow][numCol][SOUTHIND] = southblocked
        tile_walls[numRow][numCol][WESTIND]  = westblocked

    # Search for an open direction that matches the target minimum visit count (`numVisits`)
    while True:
        # Check North option
        if (northcount != 1000) and (northblocked != WALLSBLOCKED):
            if (northcount == numVisits):
                drivetrain.turn_to_heading(0, DEGREES)
                return

        # Check East option
        if (eastcount != 1000) and (eastblocked != WALLSBLOCKED):
            if (eastcount == numVisits):
                drivetrain.turn_to_heading(90, DEGREES)
                return

        # Check South option
        if (southcount != 1000) and (southblocked != WALLSBLOCKED):
            if (southcount == numVisits):
                drivetrain.turn_to_heading(180, DEGREES)
                return

        # Check West option
        if (westcount != 1000) and (westblocked != WALLSBLOCKED):
            if (westcount == numVisits):
                drivetrain.turn_to_heading(270, DEGREES)
                return

        # Increment visit threshold if no valid option was found at current level
        numVisits += 1
        wait(5, MSEC)

def drive_safe(direction, drivedist, unit):
    """Drives forward while checking boundary safety conditions, then marks the destination tile as visited."""
    global ypos
    ysouthborder = -940
    ynorthborder = 940

    ypos = location.position(Y, MM)
        
    # Prevent crossing south border boundary
    if ((ypos < ysouthborder) and (drivetrain.heading(DEGREES) == 180)):
        drivetrain.turn_for(RIGHT, 90, DEGREES)
    else:
        # Re-orient if past north border boundary
        if (ypos > ynorthborder):
            drivetrain.turn_to_heading(0, DEGREES)

        # Drive specified step distance
        drivetrain.drive_for(direction, drivedist, unit)
        
        # Update coordinate tracker and mark new tile visited
        numRow = YtoRow()
        numCol = XtoColumn()
        marktile(numRow, numCol, 1)

def main():
    """Main execution loop for maze navigation and target detection."""
    global visited_tiles, tile_dist
    global heading, rotation
    global xpos, ypos, numRow, numCol

    heading = drivetrain.heading(DEGREES)
    rotation = drivetrain.rotation(DEGREES)

    # Monitor navigation telemetry on VEXcode console
    monitor_variable("visited_tiles")
    monitor_variable("tile_walls")
    monitor_variable("tile_dist")
    monitor_variable("heading")
    monitor_variable("rotation")
    monitor_variable("xpos")
    monitor_variable("ypos")
    monitor_variable("numRow")
    monitor_variable("numCol")

    # Register start location in the grid matrix
    xpos = location.position(X, MM)
    ypos = location.position(Y, MM)
    numRow = YtoRow()
    numCol = XtoColumn()
    marktile(numRow, numCol, 1)

    # Main exploration loop (up to 1000 movement iterations)
    i = 0
    while (i < 1000): 
        wait(5, MSEC)
        i += 1

        # Quick turn if directly facing an immediate wall obstacle
        while (front_distance.get_distance(MM) < 100):
            drivetrain.turn_for(RIGHT, 90, DEGREES)

        # Evaluate surround tile weights, rotate to best path, and step forward
        rotate_to_best_dir()
        drive_safe(FORWARD, tile_dist, MM)
        
        # Stop exploration upon reaching the target destination (Red surface patch)
        if (down_eye.detect(RED)):
            break

# VR threads — Do not delete
vr_thread(main)