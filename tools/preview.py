# Import required libraries
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection as Line3D
from matplotlib.lines import Line2D

# Define machine limits (for plotting)
limits = [[0, 100], [0, 100], [0, 20]] # X, Y, Z
autoFit = False
scale = False

# Add scaling to extrusion width line thickness
mult = 1

# Load gcode and extract cartesian coordinates
path = "../gcodes/previewTest.txt"
gcode = np.loadtxt(path)
pts = gcode[:, :3]  # (N, 3) X,Y,Z
x, y, z = pts.T

# Segment gcode
segments = np.stack([pts[:-1], pts[1:]], axis=1)

# Segment distances
deltas = np.diff(pts, axis=0)
dist = np.linalg.norm(deltas, axis=1)
dist = np.maximum(dist, 1e-9)

# Extrusion amount per segment
e = np.abs(gcode[:, 6]) if gcode.shape[1] > 6 else np.zeros(len(gcode))
extrusion = e[1:]

# Find "extrusion widths"
extruding = extrusion > 0
widths = extrusion / dist

# Create figure
fig = plt.figure()
ax = fig.add_subplot(projection="3d")

# Plot extrusion lines (solid blue)
if np.any(extruding):
    ax.add_collection3d(Line3D(
        segments[extruding],
        linewidths=widths[extruding]*mult,
        colors="blue",
    ))

# Plot travel lines (dashed green)
if np.any(~extruding):
    ax.add_collection3d(Line3D(
        segments[~extruding],
        linewidths=1,
        colors="green",
        linestyles="dashed",
    ))

# Plot cartesian coordinates
ax.scatter(x, y, z, s=6)

# Format plot
ax.set(xlabel="X", ylabel="Y", zlabel="Z",
       title=f"Toolpath From {path}")

# Fit axis on min/max coordinates in gcode
if autoFit:
    ax.set_xlim(x.min(), x.max())
    ax.set_ylim(y.min(), y.max())
    ax.set_zlim(z.min(), z.max())
    x_range = x.max() - x.min()
    y_range = y.max() - y.min()
    z_range = z.max() - z.min()

# Fit axis on machine limits
else:
    ax.set_xlim(limits[0][0], limits[0][1])
    ax.set_ylim(limits[1][0], limits[1][1])
    ax.set_zlim(limits[2][0], limits[2][1])
    x_range = limits[0][1] - limits[0][0]
    y_range = limits[1][1] - limits[1][0]
    z_range = limits[2][1] - limits[2][0]

# Scale axis to limits
if scale:
    ax.set_box_aspect((x_range, y_range, z_range))

# Plot with equal size axis (cube plot)
else:
    ax.set_box_aspect((1, 1, 1))

# Add legend
ax.legend(handles=[
    Line2D([0], [0], lw=2, color="blue", label="Extrusion"),
    Line2D([0], [0], lw=2, color="green", linestyle="--", label="Travel"),
])

plt.show()