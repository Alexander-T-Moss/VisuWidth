import config as cfg, math, os


# https://manual.slic3r.org/advanced/flow-math
def e_calc(l, w=cfg.default_width, h=cfg.layer_height):
    e_area = math.pi * (1.75 / 2) ** 2
    return ((w - h) * h + math.pi * (h / 2) ** 2) * l / e_area


project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
gcode_file = open(os.path.join(project_root, "gcodes", "demo_pattern.txt"), "w", newline="\n")

# Extrusion sub-segment count
sub_segments = 20

x_step = (cfg.pat_shape[1][0] - cfg.pat_shape[0][0]) / (cfg.lines - 1)
y_step = (cfg.pat_shape[1][1] - cfg.pat_shape[0][1])

gcode_file.write('G90\n')
gcode_file.write('M83\n')
#gcode_file.write('SET_GCODE_OFFSET Z=0.03\n')
gcode_file.write('M221 S100\n')
gcode_file.write(
    f'G1 X{cfg.pat_shape[0][0]-15} Y{cfg.pat_shape[0][1]+60} Z{cfg.layer_height} F{cfg.travel_speed * 60}\n'
    'M109 S220\n'
    'G11\n'
    f'G1 Y{cfg.pat_shape[0][1]} E{e_calc(60)} F{cfg.print_speed * 60}\n'
    f'G1 X{cfg.pat_shape[0][0]} E{e_calc(15)} F{cfg.print_speed * 60}\n'
)

for i in range(cfg.lines):
    x_i = cfg.pat_shape[0][0] + i * x_step
    y_0 = cfg.pat_shape[0][1]
    y_1 = cfg.pat_shape[1][1]

    gcode_file.write(f'G1 X{x_i} Y{y_0} F{cfg.travel_speed * 60}\n')
    gcode_file.write('G11\n')

    dy = (y_1 - y_0) / sub_segments
    for s in range(1, sub_segments + 1):
        y_next = y_0 + dy * s
        gcode_file.write(
            f'G1 Y{y_next} E{e_calc(abs(dy))} F{cfg.print_speed * 60}\n'
        )

    gcode_file.write('G10\n')

gcode_file.write('M104 S0\n')
gcode_file.write('G1 X300 Y300 Z50\n')
gcode_file.write('M400\n')

gcode_file.close()

print('Gcode file updated')