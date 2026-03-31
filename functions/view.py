# Brief Description :
# Captures connected camera feed, with adjustable resolution
# both in and out for displayed previews. Containarised for
# use in other scripts
#
# References :
# https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html

# Import required libraries
import cv2, numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # project root
NPZ_DIR = BASE_DIR / "npz"

# Checkerboard calibration
try:
    data = np.load(NPZ_DIR / "checkerboard.npz")
    mtx = data["mtx"]
    dist = data["dist"]
    newcameramtx = data["newcameramtx"]
    roi_cb = data["roi"]
    checkerboard_data = True
except FileNotFoundError:
    checkerboard_data = False
    print("No checkerboard calibration data found")

# ArUco calibration
try:
    data = np.load(NPZ_DIR / "aruco.npz", allow_pickle=True)
    roi_am = data["roi"]
    M = data["M"]
    aruco_data = True
except FileNotFoundError:
    aruco_data = False
    print("No aruco calibration data found")

# Containariesed camera capture
def capture(in_res=None, out_res=None):

    # Default argument values
    if in_res is None:
        in_res = [1920, 1080]
    if out_res is not None:
        cv2.namedWindow('Preview', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Preview', out_res[0], out_res[1])

    # Get camera feed
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # Check feed opened
    if not cap.isOpened():
        print("Unable to find camera!")
        exit()

    # Override resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, in_res[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, in_res[1])

    return cap

def read_calibrated(cap, cfg):

    return cap.read() # Temporary test

    if checkerboard_data:
        ret, frame = cap.read()
        dst = cv2.undistort(frame, mtx, dist, None, newcameramtx)

        x, y, w, h = roi_cb
        dst = dst[y:y + h, x:x + w]

        dst = cv2.resize(dst, (cfg.res[0], cfg.res[1]), interpolation=cv2.INTER_LINEAR)

        return ret, dst

    return cap.read()

def read_roi(cap, cfg):

    if aruco_data:
        ret, frame = read_calibrated(cap, cfg)
        dst = cv2.warpPerspective(frame, M, cfg.res)

        return ret, dst[roi_am[0]:roi_am[1], roi_am[2]:roi_am[3]]

    return False, None

def draw_roi(img, roi, M):

    color = (0, 0, 255)
    thickness = 3
    y0, y1, x0, x1 = roi

    # ROI corners in warped/unskew image coordinates
    pts_warp = np.array([
        [x0, y0],
        [x1, y0],
        [x1, y1],
        [x0, y1],
    ], dtype=np.float32).reshape(-1, 1, 2)

    # Map back to preview using inverse homography
    Minv = np.linalg.inv(M)
    pts_prev = cv2.perspectiveTransform(pts_warp, Minv)

    # Draw polygon on preview
    cv2.polylines(img, [pts_prev.astype(np.int32)], isClosed=True,
                  color=color, thickness=thickness)

    return img

if __name__ == "__main__":

    # Example resolutions
    # res = [2560, 1440]
    res = [1920, 1080]
    # res = [1280, 720]

    view = capture(res, [640, 360])

    while True:
        ret, frame = view.read()

        if ret:
            cv2.imshow("Preview", frame)

        # Exit on escape key
        if cv2.waitKey(20) == 27:
            break

    view.release()
    cv2.destroyAllWindows()
    exit()