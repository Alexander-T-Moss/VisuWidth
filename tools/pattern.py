import preview

# Definable pattern parameters
shape = [[0.00, 0.00], [100.00, 100.00]]
hop = 2.00
layer_height = 2.00
lines = 4
em = 1.85
end_pos = [100.00, 100.00]

# Calculated pattern parameters
z = layer_height
z_hop = z + hop
y_step = (shape[1][1] - shape[0][1]) / (lines-1)
x_dist = (shape[1][0] - shape[0][0])

# Helper function to format instructions
def row(_x, _y, _z, dist=0.0):
    return [_x, _y, _z, 0.0, 0.0, 1.0, dist*em, 0, 0]

rows = [row(shape[0][0], shape[0][1], z)]

for i in range(lines):
    y = shape[0][1] + i * y_step
    
    # Extrude line
    rows.append(row(x_dist, y, z, x_dist))
    
    # End of line z hop
    rows.append(row(shape[1][0], y, z_hop))
    
    # Last line check
    if i == lines - 1:
        rows.append(row(end_pos[0], end_pos[1], z_hop))
        break
    
    # Move to start next line
    y_next = shape[0][1] + (i + 1) * y_step
    rows.append(row(shape[0][0], y_next, z_hop))
    
    # Lower for next line
    rows.append(row(shape[0][0], y_next, z))

# Where to output the generated pattern
output_path = "../gcodes/pattern.txt"

# Save the pattern
with open(output_path, "w") as f:
    for r in rows:
        line = " ".join(f"{v:.2f}" for v in r)
        f.write(line + "\n")

# Preview for sanity check
fig = preview.generate(output_path)
fig.show()