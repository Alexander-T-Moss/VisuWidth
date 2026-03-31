import config as cfg
import time


def sleep_until(target_time):
    now = time.monotonic()
    if target_time > now:
        time.sleep(target_time - now)


def monitor(target_width, width, flow, moonraker_conn, e):
    i_error = 0.0
    prev_error = 0.0
    prev_width = None

    next_update = time.monotonic()

    # Start controller once width is recorded
    while width == 0.0:
        time.sleep(0.1)

    print("Starting Controller")

    while True:
        # Control loops fixed rate
        sleep_until(next_update)
        next_update += cfg.dt

        measured_width = width.value
        desired_width = target_width.value

        # Skip 0 reads for no measurement
        if measured_width == 0:
            #print(flow.value)
            continue

        # Error
        error = desired_width - measured_width
        e.value = error

        # Proportional Term
        p_term = cfg.k_P * error

        # Integral Term (clamped)
        i_error += error * cfg.dt
        i_error = max(-50.0, min(50.0, i_error))
        i_term = cfg.k_I * i_error

        # Derivative Term
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