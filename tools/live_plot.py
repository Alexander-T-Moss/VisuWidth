import time, matplotlib.pyplot as plt, math
from pathlib import Path
import os


def plot(width, desired_width):
    plt.ion()
    fig, ax = plt.subplots()

    t_values = []
    width_values = []
    desired_width_values = []

    width_line, = ax.plot([], [], color="blue", label="Measured width", zorder=3)
    target_width_line, = ax.plot([], [], color="red", label="Target width", zorder=2)

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Extrusion Width (mm)")
    ax.legend(loc="upper left")

    start = time.time()

    data_dir = (Path(__file__).resolve().parents[1] / "data")
    data_dir.mkdir(parents=True, exist_ok=True)
    filename = time.strftime("%Y%m%d_%H%M") + ".txt"
    log_path = data_dir / filename
    log_file = open(log_path, "a", buffering=1)

    try:
        log_file.write("t_s\tmeasured_width_mm\ttarget_width_mm\n")
        log_file.flush()
        os.fsync(log_file.fileno())

        while True:
            t = time.time() - start
            w1 = width.value
            w2 = desired_width.value

            # Skip plotting 0 reads
            w1 = math.nan if w1 == 0 else w1

            log_file.write(f"{t}\t{w1}\t{w2}\n")
            log_file.flush()
            os.fsync(log_file.fileno())

            t_values.append(t)
            width_values.append(w1)
            desired_width_values.append(w2)

            # PLot last 100 seconds (oscilloscope-style)
            t_values = t_values[-10000:]
            width_values = width_values[-10000:]
            desired_width_values = desired_width_values[-10000:]

            width_line.set_data(t_values, width_values)
            target_width_line.set_data(t_values, desired_width_values)
            ax.set_xlim(max(0, t - 100), t)

            plt.pause(0.01)
    finally:
        log_file.close()
