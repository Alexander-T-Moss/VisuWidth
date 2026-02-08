import time, matplotlib.pyplot as plt, math


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

    while True:
        t = time.time() - start
        w1 = width.value
        w2 = desired_width.value

        # Skipp plotting 0 reads
        w1 = math.nan if w1 == 0 else w1

        t_values.append(t)
        width_values.append(w1)
        desired_width_values.append(w2)

        # keep last 100 seconds (oscilloscope-style)
        t_values = t_values[-10000:]
        width_values = width_values[-10000:]
        desired_width_values = desired_width_values[-10000:]

        width_line.set_data(t_values, width_values)
        target_width_line.set_data(t_values, desired_width_values)
        ax.set_xlim(max(0, t - 100), t)

        plt.pause(0.01)