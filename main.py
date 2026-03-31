# Brief Description :
# Main program that orchestrates the individual functions
#
# References :
# https://docs.python.org/3/library/multiprocessing.html
# https://pypi.org/project/MoonrakerPy/

# Import required libraries
from moonrakerpy import MoonrakerPrinter
from functions import parser, calibrate, measure, compensator, view
from multiprocessing import Process, Value
import cv2, config as cfg, time
from tools import live_plot

def main():

    # Establish connection to moonraker (printer webAPI)
    moonraker_conn = MoonrakerPrinter(cfg.printer_ip)

    # Run through print_start sequence
    parser.parse('print_start', moonraker_conn)

    # Calibration procedures
    calibrate.checkerboard(moonraker_conn, cfg) # Can comment out after being run
    calibrate.aruco(moonraker_conn, cfg)

    # Create variables accessible by processes
    width = Value('d')
    width.value = 0
    target_width = Value('d')
    target_width.value = cfg.default_width
    flow = Value('d')
    flow.value = 100

    # Font parameters for preview window
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2
    thickness = 3
    text_colour = (255, 255, 255)
    padding_x = 60
    padding_y = 60

    # Width monitor
    monitor = Process(target=measure.monitor, args=(width,))
    monitor.start()

    # Live width plotter
    plotter = Process(target=live_plot.plot, args=(width, target_width,))
    plotter.start()

    # PID flow controller
    controller = Process(target=compensator.monitor, args=(target_width, width, flow, moonraker_conn, error))
    controller.start()

    # Start the print
    print_process = Process(target=parser.parse, args=("demo_pattern", moonraker_conn))
    print_process.start()

    # Open camera feed
    cap = view.capture()

    # Main program loop
    while True:

        ret, frame = view.read_calibrated(cap, cfg)
        key = cv2.waitKey(1) & 0xFF

        # Show preview frame
        if ret:
            if view.aruco_data:
                frame = view.draw_roi(frame, view.roi_am, view.M)

            # Pull latest width and format at text
            w_mm = float(width.value)
            width_text = f"{w_mm:.3f} mm" if w_mm > 0.0 else "0.000 mm"
            (tw, th), baseline = cv2.getTextSize(width_text, font, font_scale, thickness)
            x = padding_x
            y = padding_y + th

            # Put text onto camera feed
            cv2.putText(frame, width_text, (x, y), font, font_scale,
                        text_colour, thickness, cv2.LINE_AA)

            # Pull latest flow rate and format as text
            f_percent = float(flow.value)
            flow_text = f"{f_percent:.1f} %"
            flow_y = y + th + 20

            # Put text onto camera feed
            cv2.putText(frame, flow_text, (x, flow_y), font, font_scale,
                        text_colour, thickness, cv2.LINE_AA)

            # Show camera feed in 'Preview' window
            cv2.imshow('Preview', frame)

        # Exit on escape
        if key == 27:
            plotter.terminate()
            controller.terminate()
            monitor.terminate()
            exit()

        # Change target line width when Z is pressed
        if key == ord('z') and target_width.value == cfg.default_width:
            target_width.value = 1.6
            print("Width set to 1.6mm")

        # Return target line width to default when X is pressed
        elif key == ord('x') and target_width.value != cfg.default_width:
            target_width.value = cfg.default_width
            print("Width set to default")

if __name__ == "__main__":
    main()