import numpy as np, cv2, os

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img = cv2.imread("image_04x06.png")

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Find the chess board corners
ret, corners = cv2.findChessboardCorners(gray, (5, 6), None)

# If found, add object points, image points (after refining them)
if ret == True:

    objpoints.append(objp)

    corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    imgpoints.append(corners2)

    vis = img.copy()

    pattern_size = (5, 6)  # cols, rows you passed to findChessboardCorners
    cols, rows = pattern_size

    pts = corners2.reshape(rows, cols, 2)

    # draw rows
    for r in range(rows):
        for c in range(cols - 1):
            p1 = tuple(np.round(pts[r, c]).astype(int))
            p2 = tuple(np.round(pts[r, c + 1]).astype(int))
            cv2.line(vis, p1, p2, (0, 0, 255), 5, cv2.LINE_AA)

    # draw cols
    for c in range(cols):
        for r in range(rows - 1):
            p1 = tuple(np.round(pts[r, c]).astype(int))
            p2 = tuple(np.round(pts[r + 1, c]).astype(int))
            cv2.line(vis, p1, p2, (0, 0, 255), 5, cv2.LINE_AA)

    # optionally also draw corners
    for (x, y) in corners2.reshape(-1, 2):
        cv2.circle(vis, (int(round(x)), int(round(y))), 10, (255, 0, 0), -1)

    cv2.imshow("img", vis)
    cv2.waitKey(0)

