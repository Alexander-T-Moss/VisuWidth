# Import required libraries
import config as cfg
import time

# Helper function
def sleep_until(target_time):
    now = time.monotonic()
    if target_time > now:
        time.sleep(target_time - now)

# PID controller (ran as a process)
def monitor(target_width, width, flow, moonraker_conn, e):

    # Controller variables
    i_error = 0.0
    prev_error = 0.0
    prev_width = None

    next_update = time.monotonic()

    # Only start controller once non-zero width is recorded
    while width == 0.0:
        time.sleep(0.1)
    print("Starting Controller")

    # PID Loop
    while True:

        # Control loop fixed update rate
        sleep_until(next_update)
        next_update += cfg.dt

        # Get latest width measurement
        measured_width = width.value
        desired_width = target_width.value

        # Skip zero width measurements
        if measured_width == 0:
            continue

        # Calculate error in extrusion width
        error = desired_width - measured_width
        e.value = error

        # Proportional term
        p_term = cfg.k_P * error

        # Integral term (clamped)
        i_error += error * cfg.dt
        i_error = max(-50.0, min(50.0, i_error))
        i_term = cfg.k_I * i_error

        # Derivative term
        if prev_width is None:
            d_error = 0.0
        else:
            d_error = (error - prev_error) / cfg.dt
        d_term = cfg.k_D * d_error

        # Update previous values
        prev_error = error
        prev_width = measured_width

        # PID output
        flow.value = flow.value + p_term + i_term + d_term
        flow.value = max(25.0, min(200.0, flow.value))
        moonraker_conn.send_gcode(f"M221 S{flow.value}")