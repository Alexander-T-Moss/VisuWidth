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
    #parser.parse('print_start', moonraker_conn)

    # Calibration procedures
    #calibrate.checkerboard(moonraker_conn, cfg)
    #calibrate.aruco(moonraker_conn, cfg)

    # Create a float variable to store width measurement
    width = Value('d')
    width.value = 0
    target_width = Value('d')
    target_width.value = cfg.default_width

    # Start the width monitor
    monitor = Process(target=measure.monitor, args=(width,))
    monitor.start()

    # Start the live width plotter
    plotter = Process(target=live_plot.plot, args=(width, target_width,))
    plotter.start()

    # Start PID controller
    controller = Process(target=compensator.monitor, args=(target_width, width, moonraker_conn))
    controller.start()

    # Start the print
    print_process = Process(target=parser.parse, args=("demo_pattern", moonraker_conn))
    print_process.start()

    cap = view.capture()

    # Main program loop
    while True:
        ret, frame = view.read_calibrated(cap, cfg)
        key = cv2.waitKey(1) & 0xFF

        # Show preview frame
        if ret:
            cv2.imshow('Preview', frame)

        # Exit on escape
        if key == 27:
            plotter.terminate()
            controller.terminate()
            monitor.terminate()
            exit()

        # Increase target line width when Z is pressed
        if key == ord('z') and target_width.value == cfg.default_width:
            target_width.value = cfg.default_width * 0.75
            print("Width set to 0.75x")

        # Return target line width to default when X is pressed
        elif key == ord('x') and target_width.value != cfg.default_width:
            target_width.value = cfg.default_width
            print("Width set to 1.0x")


if __name__ == "__main__":
    main()