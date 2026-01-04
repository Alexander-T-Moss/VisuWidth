import numpy as np
import matplotlib.pyplot as plt

gcode = "../gcodes/0.txt"
data = np.loadtxt(gcode)
x, y, z = data[:, :3].T
e = data[:, 6]

dx, dy, dz = np.diff([x, y, z], axis=1)
move_len = np.sqrt(dx*dx + dy*dy + dz*dz)
e_seg = e[1:]

ratio = np.full_like(move_len, np.nan, dtype=float)
nonzero = (move_len > 0) & (e_seg != 0)
ratio[nonzero] = e_seg[nonzero] / move_len[nonzero]

avg_ratio = np.nanmean(ratio)
valid = ~np.isnan(ratio)

plt.figure()
plt.plot(ratio[valid], marker="o", linewidth=1)

plt.xlabel("Instruction Index")
plt.ylabel("EM Value")
plt.title("EM Value Across Instructions")
plt.grid(True, alpha=0.3)
plt.ylim(round(avg_ratio, 1)-0.2, round(avg_ratio, 1)+0.2)

plt.text(
    0.98, 0.98,
    f"Average: {avg_ratio:.4g}",
    transform=plt.gca().transAxes,
    ha="right",
    va="top"
)

plt.tight_layout()
plt.show()