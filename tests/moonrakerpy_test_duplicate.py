import moonrakerpy as moonpy
import math

EM = 2
layer_height = 0.6
z_offset = 0.2
layer_width = 1.2

# https://manual.slic3r.org/advanced/flow-math
def e_calc(l, w = layer_width, h = layer_height):
    eArea = math.pi * (1.75/2)**2
    return ((w-h)*h + math.pi*(h/2)**2)*l/eArea

printer = moonpy.MoonrakerPrinter('http://trident.local')
#printer.send_gcode('G28')
#printer.send_gcode('Z_TILT_ADJUST')
#printer.send_gcode('BED_MESH_CALIBRATE')

# https://www.klipper3d.org/G-Codes.html
#printer.send_gcode(f'G1 X150 Y50 Z{layer_height+z_offset} F6000')
#printer.send_gcode('M109 S215')
#printer.send_gcode('G1 E4') # Prime nozzle
#printer.send_gcode(f'G1 X150 Y250 E{e_calc(200)*EM} F600')
#printer.send_gcode('G1 E-2')
#printer.send_gcode('G1 Z5')
#printer.send_gcode('M104 S150')
#printer.send_gcode('G1 X300 Y300 F6000')

printer.send_gcode('M221 S101')
resp = printer.query_status({"gcode_move": ["extrude_factor"]})
print(resp["status"]["gcode_move"]["extrude_factor"])
printer.send_gcode('M221 S100')
print(printer.query_status('extruder_factor'))

