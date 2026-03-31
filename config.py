# Brief Description :
# All user-changeable parameters consolidated
# to a single .py file

# Compensator PID parameters
k_P = 15
k_I = 0
k_D = 5
dt = 2

# Camera resolution
res = [1920, 1080]
roi_res = 400

# Chessboard search bounds
check_start = [0, 257.0, 15.0]
check_end = [39, 289.0, 15.0]
check_mesh = [6, 6]

# Printer specific parameters
printer_ip = 'http://trident.local'
min_width = 0.4 # mm
max_width = 3 # mm

# Test pattern parameters
pat_shape = [[30.0, 30.0], [270.0, 260.0]]
layer_height = 0.6 # mm
lines = 11
default_width = 2.0 # mm
print_speed = 10 # mm/s
travel_speed = 300 # mm/s

# Place aruco mark in ROI from camera perspective
# Z needs to match layer_height
aruco_location = [292.20, 14.70, layer_height]

# Length (mm) of the Aruco marker side
aruco_dim = 7.96