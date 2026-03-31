# Brief Description :
# Using an ArUco marker, determines the skew correction
# factor M and ROI, saving results to a NPZ in npz directory
#
# References :
# https://www.geeksforgeeks.org/computer-vision/detecting-aruco-markers-with-opencv-and-python-1/
# https://docs.opencv.org/4.x/da/d6e/tutorial_py_geometric_transformations.html
# https://docs.opencv.org/4.x/dd/d92/tutorial_corner_subpixels.html

# Import required libraries
import cv2, time, os, glob
import numpy as np
import functions.view as view
from functions.view import read_calibrated

# Define ArUco dictionary
arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

# Create ArUco detector with default parameters
params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(arucoDict, params)

# Sub-pixel refinement criteria
# (https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html)
subPixCrit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Find npz directory to save checkerboard images
checkerboard_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "images",
    "checkerboards"
)

# Define checkerboard search parameters
pattern = (5,6)
crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Ideal checkerboard locations
obj_pt = np.zeros((pattern[0] * pattern[1], 3), np.float32)
obj_pt[:, :2] = np.mgrid[0:pattern[0], 0:pattern[1]].T.reshape(-1, 2)

# Stores for recorded checkerboard positions
obj_pts = []
img_pts = []

# Checkerboard calibration function
def checkerboard(moonraker_conn, cfg, npz_path='npz/checkerboard.npz'):

    # Calculate number of checkerboard images to be captured
    meshCount = cfg.check_mesh[0]*cfg.check_mesh[1]
    print(f"Scanning checkerboard\nMesh points: {meshCount}")

    # Clear checkerboard directory if it exists
    if os.path.isdir(checkerboard_dir):
        for f in os.listdir(checkerboard_dir):
            fp = os.path.join(checkerboard_dir, f)
            if os.path.isfile(fp):
                os.remove(fp)
    else:
        os.makedirs(checkerboard_dir, exist_ok=True)

    # Determine mesh step size
    x_step = (cfg.check_end[0] - cfg.check_start[0]) / (cfg.check_mesh[0] - 1)
    y_step = (cfg.check_end[1] - cfg.check_start[1]) / (cfg.check_mesh[1] - 1)

    # Put printer into relative positioning
    moonraker_conn.send_gcode('G90')

    # Open camera feed
    cap = view.capture(cfg.res)

    # Iterate through mesh points
    for yi in range(cfg.check_mesh[1]):
        y = cfg.check_start[1] + yi * y_step

        for xi in range(cfg.check_mesh[0]):
            x = cfg.check_start[0] + xi * x_step

            # Move to current mesh point
            moonraker_conn.send_gcode(f'G1 X{x:.3f} Y{y:.3f} Z{cfg.check_end[2]:.3f} F6000')
            moonraker_conn.send_gcode('M400')
            time.sleep(0.2)

            # Capture frame
            ret, frame = cap.read()
            if ret:
                fname = f'image_{xi:02d}x{yi:02d}.png'

                # Save frame for later
                save = cv2.imwrite(os.path.join(checkerboard_dir, fname), frame)
                if not save:
                    print(f'Failed to save image: {xi:02d}x{yi:02d}')

    # Calibrate camera from collected images
    print('Calibrating...')

    # Find all stored image paths
    img_paths = sorted(
        glob.glob(os.path.join(checkerboard_dir, "*.png")))

    # Detection variables
    detects = 0
    grey = None

    # Iterate through stored images
    for path in img_paths:
        img = cv2.imread(path)
        grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Search for checkerboard in image
        found, corners = cv2.findChessboardCorners(grey, pattern, None)
        if found:
            detects += 1

            # Store checkerboard corner points
            obj_pts.append(obj_pt)
            img_pts.append(cv2.cornerSubPix(grey, corners, (11, 11), (-1, -1), crit))

    print(f'Detected {detects}/{len(img_paths)} checkerboards')

    # Determine camera correction matrix
    if grey is not None and detects > 2/3 * meshCount:
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_pts, img_pts, grey.shape[::-1], None, 4, None, None,
                                                           cv2.CALIB_ZERO_TANGENT_DIST,
                                                           criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30,
                                                                     2e-16))
        h, w = grey.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

        # Save calibrated camera matrix as .npz
        np.savez(npz_path, mtx=mtx, dist=dist, newcameramtx=newcameramtx, roi=roi)

        print('New camera matrix calculated and saved')

        # Apply new camera matrix
        view.mtx = mtx
        view.dist = dist
        view.newcameramtx = newcameramtx
        view.roi = roi
        view.checkerboard_data = True
        print('Checkerboard calibration reloaded')

    else:
        print('Insuffiecent number of checkerboards found')

    cap.release()

# Aruco marker calibration function
def aruco(moonraker_conn, cfg):

    # Move to Aruco marker
    print('Scanning Aruco Marker')
    moonraker_conn.send_gcode(f'G0 X{cfg.aruco_location[0]} Y{cfg.aruco_location[1]} Z{cfg.aruco_location[2]} F{cfg.travel_speed*60}')
    moonraker_conn.send_gcode('M400')
    time.sleep(1) # Allow camera to refocus

    # Open camera
    cap = view.capture(cfg.res)

    # Define reference points to calibrate against
    ref_pts = np.float32([
        [cfg.res[0] / 2 - cfg.roi_res/2, cfg.res[1] / 2 - cfg.roi_res/2],
        [cfg.res[0] / 2 + cfg.roi_res/2, cfg.res[1] / 2 - cfg.roi_res/2],
        [cfg.res[0] / 2 + cfg.roi_res/2, cfg.res[1] / 2 + cfg.roi_res/2],
        [cfg.res[0] / 2 - cfg.roi_res/2, cfg.res[1] / 2 + cfg.roi_res/2]
    ])

    # Calibrate off Aruco marker
    calibrated = False
    while not calibrated:

        # Pull latest frame
        ret, frame = read_calibrated(cap, cfg)

        # Check if pulled frame successfully
        if not ret:
            print('Unable to retrieve camera frame')
            break

        # Search for Aruco maker
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        crnrs, ids, _ = detector.detectMarkers(grey)

        # Bypass aruco calibration with esc
        if cv2.waitKey(1) & 0xFF == 27:
            break

        # Calibrate skew if correct marker is found
        if ids is not None:
            if 18 in ids:
                # Refine location of Aruco marker corners
                print('Detected marker')
                crnrsSubPix = cv2.cornerSubPix(grey, crnrs[0].astype(np.float32),
                                               (11, 11), (-1, -1), subPixCrit)

                # Calculate perspective transform
                M = cv2.getPerspectiveTransform(crnrsSubPix.reshape(4, 2).astype(np.float32), ref_pts)
                print('Transform calculated')

                # Calculate ROI crop
                y_min = int(np.floor(np.min(ref_pts[:, 1])))
                y_max = int(np.ceil(np.max(ref_pts[:, 1])))
                x_min = int(np.floor(np.min(ref_pts[:, 0])))
                x_max = int(np.ceil(np.max(ref_pts[:, 0])))
                roi = np.array([y_min, y_max, x_min, x_max], dtype=np.int32)
                print('ROI calculated')

                # Save and exit calibration
                np.savez('npz/aruco.npz', roi=roi, M=M)
                print('Calibration saved to ~/npz/aruco.npz')

                # Apply camera calibration
                view.roi_am = roi
                view.M = M
                view.aruco_data = True
                calibrated=True
                print('Aruco calibration reloaded')

    cap.release()
    cv2.destroyAllWindows()

# Run checkerboard calibration
if __name__ == "__main__":

    # Import required libraries
    import moonrakerpy as moonpy
    import config as cfg

    # Find npz directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    npz_dir = os.path.join(script_dir, "..", "npz")
    os.makedirs(npz_dir, exist_ok=True)

    # Format path to npz save file
    npz_path = os.path.join(npz_dir, "checkerboard.npz")

    # Run the calibrations
    moonraker_conn = moonpy.MoonrakerPrinter(cfg.printer_ip)
    checkerboard(moonraker_conn, cfg, npz_path)

    cv2.destroyAllWindows()
    exit()