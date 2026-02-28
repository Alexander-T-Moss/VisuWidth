# Compensator PID parameters
k_P = 15
k_I = 0
k_D = 5

# Other compensator parameters
dt = 2

# Camera resolution
res = [1920, 1080]
roi_res = 400

# Ceckerboard search bounds
check_start = [0, 247.0, 15.0]
check_end = [41, 291.0, 15.0]
check_mesh = [6, 8]

printer_ip = 'http://trident.local'

min_width = 0.4
max_width = 3

# Pattern paramenters
pat_shape = [[30.0, 30.0], [270.0, 260.0]]
layer_height = 0.6
lines = 11
default_width = 1.2
print_speed = 10 # mm/s
travel_speed = 300 # mm/s

# Place aruco mark in ROI from camera perspective
# Z needs to match layer_height below
aruco_location = [290.70, 15.10, layer_height]

# Length (mm) of the Aruco marker side
aruco_dim = 8.46