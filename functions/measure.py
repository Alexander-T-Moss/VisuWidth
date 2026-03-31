# Import required libraries
import cv2, numpy as np, config as cfg, time
from functions import view
from collections import deque

# Masking function
def mask(img, min_area=1500.0):

   # OTSU binary thresholding
   gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
   blr = cv2.GaussianBlur(gry, (5, 5), 0)
   otsu = cv2.threshold(blr, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

   cv2.imshow('DENOISED', blr)
   cv2.imshow('OTSU', otsu)

   # Morphology clean (replaced with contour filtering):
   # (https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html)
   #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
   #otsu = cv2.morphologyEx(otsu, cv2.MORPH_OPEN, kernel, iterations=1)
   #otsu = cv2.morphologyEx(otsu, cv2.MORPH_CLOSE, kernel, iterations=2)

   # Contour filtering
   msk = np.zeros(img.shape[:2], np.uint8)
   cnts, rnk = cv2.findContours(otsu, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
   for i, cnt in enumerate(cnts):
       if rnk[0][i][2] == -1: # Filters out contours that contain contours
           if cv2.contourArea(cnt) > min_area: # Filters out contours below min_area
               cv2.drawContours(msk, [cnt], 0, 255, -1)

   cv2.imshow("MASK", msk)
   return msk

# Canny edge detection and edge seperation measurer
def measure_edges(image, n = 1.0):

   # Canny edge detection
   # (https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html)
   canny = cv2.Canny(image, 0, 255)
   cv2.imshow('CANNY', canny)

   # Stores for edges and rows from image
   edges, rows = [], []

   # Find pairs of 255 (edges as white pixels)
   for y, px in enumerate(canny):
       pts = np.where(px == 255)[0]
       if len(pts) == 2:
           edges.append(pts)
           rows.append(y)

   # Convert edges, rows to numpy arrays for handling
   edges, rows = np.array(edges), np.array(rows)

   # Check if edges are long enough to be valid
   # (2/3 of ROI needs a detected edge)
   min_length = 2*cfg.roi_res/3
   if len(edges) <= min_length:
       return 0, None, None

   # Find seperation of edges
   diffs = np.abs(edges[:, 0] - edges[:, 1])

   # Calculate mean and standard deviation of seperations
   mean = np.mean(diffs)
   std = np.std(diffs)

   # Remove differences outside 1 standard deviation
   mask = (diffs > mean - n * std) & (diffs < mean + n * std)
   filtered_diffs = diffs[mask]
   filtered_edges = edges[mask]
   filtered_rows = rows[mask]

   # Catch no valid widths detected
   if len(filtered_diffs) == 0:
       return 0, None, None

   return np.mean(filtered_diffs), filtered_edges, filtered_rows

# Edge measuring function (ran as a process)
def monitor(width):

   # Open webcam feed
   cap = view.capture()

   # Work out size of pixels (mm)
   px_length = cfg.aruco_dim / cfg.roi_res

   # Text on image parameters
   font = cv2.FONT_HERSHEY_SIMPLEX
   font_scale = 0.8
   thickness = 1
   margin = 10
   line_gap = 8
   colour = (255, 255, 255)
   time_text = '0ms'

   # Running average parameters
   mean_width_count = 10
   widths = deque(maxlen=mean_width_count)

   # Filtering parameters
   step_threshold = 0.2
   holdoff = 0.4
   zero_read_time = None
   non_zero_read = False

   # Start monitor
   while True:

       t0 = time.perf_counter()
       ret, frame = view.read_roi(cap, cfg)

       if ret:

           # Mask and measure image (above functions)
           msk = mask(frame)
           dst, edges, rows = measure_edges(msk, 1.5)
           dst *= px_length
           width_text = f"{dst:.3f} mm"

           # Update width (if all filter checks pass)
           now = time.perf_counter()

           if len(widths) == mean_width_count:
               prev_width = np.mean(widths, dtype=float)
               valid_step = abs(dst - prev_width) < step_threshold # Change within max step
               valid_range = cfg.min_width < prev_width < cfg.max_width # Width in expected range

               ok = (valid_step and valid_range)
               out = float(prev_width) if ok else 0.0

               # Handle zero width measurements
               if out == 0.0:
                   width.value = 0.0
                   zero_read_time = now
                   non_zero_read = False

               # Ignore initial extrusion inconsistency (pressure equalising)
               # with delay in outputting measured widths
               else:
                   if zero_read_time is None:
                       width.value = out
                   else:
                       if not non_zero_read:
                           non_zero_read = True
                       elif (now - zero_read_time) >= holdoff:
                           width.value = out

           # Store width measurement
           widths.append(dst)

           # Draw edge lines onto preview image
           if edges is not None and rows is not None:
               for (left, right), y in zip(edges, rows):
                   cv2.circle(frame, (left, y), 2, (0, 0, 255), -1)
                   cv2.circle(frame, (right, y), 2, (0, 255, 0), -1)

           # Add information text to preview frame
           (w1, h1), _ = cv2.getTextSize(width_text, font, font_scale, thickness)
           (w2, h2), _ = cv2.getTextSize(time_text, font, font_scale, thickness)
           x = margin
           y_top = margin

           # Measured width
           y1 = y_top + h1
           cv2.putText(frame, width_text, (x, y1), font, font_scale, colour,
                       thickness, cv2.LINE_AA)

           # Time to measure
           y2 = y1 + line_gap + h2
           cv2.putText(frame, time_text, (x, y2), font, font_scale, colour,
                       thickness, cv2.LINE_AA)
           t1 = time.perf_counter()
           ms = (t1 - t0) * 1000
           time_text = f"{ms:.2f} ms"

           # Show preview frames
           cv2.imshow('Preview', frame)

       # Exit on escape key
       if cv2.waitKey(20) == 27:
           break

   cap.release()