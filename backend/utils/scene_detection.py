
import cv2
import numpy as np

def detect_scene_changes(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_diffs = []
    ret, prev_frame = cap.read()
    while ret:
        ret, curr_frame = cap.read()
        if not ret:
            break
        diff = cv2.absdiff(prev_frame, curr_frame)
        non_zero_count = np.count_nonzero(diff)
        frame_diffs.append(non_zero_count)
        prev_frame = curr_frame
    cap.release()
    return frame_diffs
