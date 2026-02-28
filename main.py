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
    calibrate.aruco(moonraker_conn, cfg)

    # Create a float variable to store width measurement
    width = Value('d')
    width.value = 0
    target_width = Value('d')
    target_width.value = cfg.default_width
    flow = Value('d')
    flow.value = 100

    error = Value('d')

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2
    thickness = 3
    text_colour = (255, 255, 255)

    padding_x = 60
    padding_y = 60

    # Start the width monitor
    monitor = Process(target=measure.monitor, args=(width,))
    monitor.start()

    # Start the live width plotter
    #plotter = Process(target=live_plot.plot, args=(width, target_width,))
    #plotter.start()

    temp_plotter = Process(target=live_plot.plot, args=(flow, error))
    temp_plotter.start()

    # Start PID controller
    controller = Process(target=compensator.monitor, args=(target_width, width, flow, moonraker_conn, error))
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
            if view.aruco_data:
                frame = view.draw_roi(frame, view.roi_am, view.M)

            w_mm = float(width.value)
            width_text = f"{w_mm:.3f} mm" if w_mm > 0.0 else "0.000 mm"

            # measure text size
            (tw, th), baseline = cv2.getTextSize(width_text, font, font_scale, thickness)

            # OpenCV anchors text at the BASELINE, not the top
            x = padding_x
            y = padding_y + th

            cv2.putText(frame, width_text, (x, y), font, font_scale,
                        text_colour, thickness, cv2.LINE_AA)

            f_percent = float(flow.value)
            flow_text = f"{f_percent:.1f} %"

            # position directly beneath width text
            flow_y = y + th + 20  # 20px vertical spacing

            cv2.putText(frame, flow_text, (x, flow_y), font, font_scale,
                        text_colour, thickness, cv2.LINE_AA)

            cv2.imshow('Preview', frame)

        # Exit on escape
        if key == 27:
            plotter.terminate()
            #controller.terminate()
            monitor.terminate()
            exit()

        # Increase target line width when Z is pressed
        if key == ord('z') and target_width.value == cfg.default_width:
            target_width.value = cfg.default_width * 1.4
            print("Width set to 1.4x")

        # Return target line width to default when X is pressed
        elif key == ord('x') and target_width.value != cfg.default_width:
            target_width.value = cfg.default_width
            print("Width set to 1.0x")


if __name__ == "__main__":
    main()