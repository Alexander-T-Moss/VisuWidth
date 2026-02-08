import math
import os

EM = 2
layer_height = 0.6
z_offset = 0.2
layer_width = 1.2

# https://manual.slic3r.org/advanced/flow-math
def e_calc(l, w=layer_width, h=layer_height):
    eArea = math.pi * (1.75 / 2) ** 2
    return ((w - h) * h + math.pi * (h / 2) ** 2) * l / eArea

# Collect G-code commands instead of sending them
gcode_commands = []

# https://www.klipper3d.org/G-Codes.html
gcode_commands.append(f'G1 X150 Y50 Z{layer_height + z_offset} F6000')
gcode_commands.append('M109 S215')
gcode_commands.append('G1 E4')  # Prime nozzle
gcode_commands.append(f'G1 X150 Y250 E{e_calc(200) * EM} F600')
gcode_commands.append('G1 E-2')
gcode_commands.append('G1 Z5')
gcode_commands.append('M104 S150')
gcode_commands.append('G1 X300 Y300 F6000')

# Ensure output directory exists
output_dir = 'gcodes'
os.makedirs(output_dir, exist_ok=True)

# Write G-code to file
output_path = os.path.join(output_dir, 'pattern_gcode.gcode')
with open(output_path, 'w') as f:
    for line in gcode_commands:
        f.write(line + '\n')
