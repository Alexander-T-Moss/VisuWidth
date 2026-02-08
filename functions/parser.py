# Import required libraries
import os, config as cfg

# Sends commands in filename to printer via moonraker
def parse(filename, moonraker_conn):

    # Find filename.txt
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        gcode_path = os.path.join(base_dir, "gcodes", f"{filename}.txt")

    # If it can't find the specified file
    except FileNotFoundError:
        print(f"Could not find gcode file {filename}.txt")
        exit(1)

    # Send commands in file to moonraker_conn
    print(f'Parsing {filename}.txt')
    with open(gcode_path, "r") as f:
        for line in f:
            try:
                moonraker_conn.send_gcode(line.strip())
            except Exception as e:
                print(e)
        # Stop parser finishing before last command executed
        moonraker_conn.send_gcode('M400')

    # Send confirmation message
    print(f'{filename}.txt parsed')