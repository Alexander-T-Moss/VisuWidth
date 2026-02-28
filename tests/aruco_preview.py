import cv2 as cv
import numpy as np

# Define the dictionary we want to use
arucoDict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)

# Create ArUco detector with default parameters
params = cv.aruco.DetectorParameters()
detector = cv.aruco.ArucoDetector(arucoDict, params)

def draw_aruco_manually(img, corners, ids):
    """
    Draws clearer, manual overlays for detected ArUco markers:
      - thick polygon outline
      - corner dots with labels (TL/TR/BR/BL)
      - center crosshair
      - id label with a filled background
    """
    if ids is None or corners is None:
        return

    ids = ids.flatten()

    for marker_corners, marker_id in zip(corners, ids):
        # marker_corners shape: (1, 4, 2) -> (4, 2)
        pts = marker_corners.reshape(4, 2)

        # Convert to integer pixel coords for drawing
        p = pts.astype(int)

        # Order is OpenCV ArUco standard: TL, TR, BR, BL
        tl, tr, br, bl = p[0], p[1], p[2], p[3]

        # 1) Thick outline (closed polygon)
        cv.polylines(img, [p], isClosed=True, color=(0, 255, 255), thickness=3, lineType=cv.LINE_AA)

        # 2) Corner dots + corner labels
        corner_names = [("TL", tl), ("TR", tr), ("BR", br), ("BL", bl)]
        for name, pt in corner_names:
            cv.circle(img, tuple(pt), 6, (0, 0, 255), -1, lineType=cv.LINE_AA)
            cv.putText(img, name, (pt[0] + 8, pt[1] - 8),
                       cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv.LINE_AA)

        # 3) Center crosshair
        center = pts.mean(axis=0).astype(int)
        cx, cy = int(center[0]), int(center[1])
        cv.drawMarker(img, (cx, cy), (255, 0, 0), markerType=cv.MARKER_CROSS,
                      markerSize=20, thickness=2, line_type=cv.LINE_AA)

        # 4) ID label with filled background near top-left corner
        label = f"ID: {marker_id}"
        (tw, th), baseline = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        x, y = int(tl[0]), int(tl[1])

        # Place label slightly above TL; if that goes off-screen, place below
        y_text = y - 10
        if y_text - th - baseline < 0:
            y_text = y + th + 10

        # Background rectangle
        top_left = (x, y_text - th - baseline)
        bottom_right = (x + tw + 10, y_text + baseline)
        cv.rectangle(img, top_left, bottom_right, (0, 0, 0), thickness=-1)

        # Text
        cv.putText(img, label, (x + 5, y_text),
                   cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv.LINE_AA)

view = cv.VideoCapture(0)
if not view.isOpened():
    print("Cannot open camera")
    raise SystemExit

while True:
    ret, frame = view.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    corners, ids, rejected = detector.detectMarkers(gray)

    # Replace cv.aruco.drawDetectedMarkers(...) with manual plotting
    draw_aruco_manually(frame, corners, ids)

    cv.imshow("Webcam View", frame)

    if cv.waitKey(20) == 27:  # ESC
        break

view.release()
cv.destroyAllWindows()
