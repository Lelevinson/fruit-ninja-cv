import cv2
import mediapipe as mp
import time
import math
from threading import Thread
from collections import deque


class WebcamStream:
    """
    Threaded webcam capture to ensure the main loop never blocks on I/O.
    Always holds the most recent frame.
    """

    def __init__(self, src=0, width=640, height=480):
        # cv2.CAP_DSHOW is required on Windows to avoid MSMF errors and reduce initialization latency
        self.stream = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self.thread = None
        self.stopped = False
        self.grabbed = False
        self.frame = None
        self.read_fail_count = 0

        # Read first frame to ensure it's working
        if not self.stream.isOpened():
            print(
                "[Camera] Unable to open webcam. Check camera permissions/device usage."
            )
            self.stopped = True
        else:
            self.grabbed, self.frame = self.stream.read()
            if not self.grabbed or self.frame is None:
                print("[Camera] Webcam opened but no frame available yet.")

    def start(self):
        if self.stopped:
            return self
        if self.thread and self.thread.is_alive():
            return self
        self.thread = Thread(target=self.update, args=(), daemon=True)
        self.thread.start()
        return self

    def update(self):
        while not self.stopped:
            grabbed, frame = self.stream.read()
            if grabbed and frame is not None:
                self.grabbed = True
                self.frame = frame
                self.read_fail_count = 0
                continue

            self.grabbed = False
            self.read_fail_count += 1
            if self.read_fail_count in (1, 60):
                print("[Camera] Frame read failed. Retrying...")
            time.sleep(0.005)

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)
        self.stream.release()


class HandTracker:
    def __init__(self, detection_con=0.6, track_con=0.6):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,  # Only track one hand for performance
            model_complexity=1,  # Higher-fidelity model for smoother landmarks
            min_detection_confidence=detection_con,
            min_tracking_confidence=track_con,
        )

        # Tracking State
        self.prev_x, self.prev_y = 0, 0
        self.prev_time = time.time()
        self.missing_frames = 0
        self.max_missing_frames = 3

        # Adaptive smoothing params tuned for lower latency.
        self.alpha = 0.65
        self.alpha_slow = 0.68
        self.alpha_fast = 0.88
        self.fast_move_threshold = 60
        self.alpha_blend = 0.2

        # Smoothed velocity used for slicing stability.
        self.velocity_history = deque(maxlen=5)

        # Pinch-hold state machine for knife stop.
        self.knife_stop_active = False
        self.knife_enter_count = 0
        self.knife_exit_count = 0
        self.knife_enter_frames = 5
        self.knife_exit_frames = 3
        self.knife_enter_velocity = 350

    def is_palm_open(self, lm_list):
        """
        Heuristic to check if hand is open.
        Checks if tips of fingers (8, 12, 16, 20) are far from wrist (0)
        and spread out.
        """
        if not lm_list:
            return False

        # 1. Check if all fingers are extended (tipy < pipy usually for upright hand,
        # but rotation matters. Better: Dist(Tip, Wrist) > Dist(Pip, Wrist))
        # Simple heuristic: Check distance of tips from wrist
        wrist = lm_list[0]
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]

        open_fingers = 0
        for i in range(4):
            tip = lm_list[tips[i]]
            pip = lm_list[pips[i]]

            # Simple check: Tip is further from wrist than PIP
            dist_tip = math.hypot(tip[1] - wrist[1], tip[2] - wrist[2])
            dist_pip = math.hypot(pip[1] - wrist[1], pip[2] - wrist[2])

            if dist_tip > dist_pip:
                open_fingers += 1

        return open_fingers == 4  # Thumb is tricky, ignoring for "Palm"

    def _is_pinching(self, lm_list):
        """Returns True if thumb and index fingertips are close relative to hand size."""
        if not lm_list or len(lm_list) < 18:
            return False

        thumb_tip = lm_list[4]
        index_tip = lm_list[8]
        index_mcp = lm_list[5]
        pinky_mcp = lm_list[17]

        pinch_dist = math.hypot(
            thumb_tip[1] - index_tip[1], thumb_tip[2] - index_tip[2]
        )
        hand_scale = math.hypot(
            index_mcp[1] - pinky_mcp[1], index_mcp[2] - pinky_mcp[2]
        )

        if hand_scale <= 1:
            return False

        return pinch_dist < (hand_scale * 0.45)

    def _update_knife_stop(self, pinching, velocity):
        """Debounced pinch hold with hysteresis to avoid flickering state."""
        enter_condition = pinching and velocity < self.knife_enter_velocity

        if not self.knife_stop_active:
            if enter_condition:
                self.knife_enter_count += 1
                if self.knife_enter_count >= self.knife_enter_frames:
                    self.knife_stop_active = True
                    self.knife_enter_count = 0
                    self.knife_exit_count = 0
            else:
                self.knife_enter_count = 0
        else:
            if not pinching:
                self.knife_exit_count += 1
                if self.knife_exit_count >= self.knife_exit_frames:
                    self.knife_stop_active = False
                    self.knife_enter_count = 0
                    self.knife_exit_count = 0
            else:
                self.knife_exit_count = 0

        return self.knife_stop_active

    def find_position(self, frame, detect_palm_pause=True):
        """
        Processes frame and returns:
        cx, cy, velocity, is_knife_stopped
        """
        # Optimization: Pass by reference
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_rgb.flags.writeable = False

        results = self.hands.process(img_rgb)

        timestamp = time.time()
        dt = timestamp - self.prev_time
        if dt <= 0:
            dt = 0.016
        elif dt > 0.1:
            dt = 0.1

        is_knife_stopped = False

        cx, cy, velocity = None, None, 0.0

        if results.multi_hand_landmarks:
            self.missing_frames = 0
            hand_lms = results.multi_hand_landmarks[0]
            h, w, c = frame.shape

            # Re-convert to list of [id, x, y] (pixels)
            pixel_lms = []
            for lm in hand_lms.landmark:
                pixel_lms.append(
                    [0, int(lm.x * w), int(lm.y * h)]
                )  # ID not needed in index, just position

            # Index Finger Tip is ID 8
            raw_x, raw_y = pixel_lms[8][1], pixel_lms[8][2]

            # --- Adaptive Smoothing (Copy from before) ---
            dist = math.hypot(raw_x - self.prev_x, raw_y - self.prev_y)
            if dist > self.fast_move_threshold:
                target_alpha = self.alpha_fast
            else:
                target_alpha = self.alpha_slow

            self.alpha += (target_alpha - self.alpha) * self.alpha_blend

            if self.prev_x == 0 and self.prev_y == 0:
                smooth_x, smooth_y = raw_x, raw_y
            else:
                smooth_x = self.alpha * raw_x + (1 - self.alpha) * self.prev_x
                smooth_y = self.alpha * raw_y + (1 - self.alpha) * self.prev_y

            move_dist = math.hypot(smooth_x - self.prev_x, smooth_y - self.prev_y)
            raw_velocity = move_dist / dt

            self.velocity_history.append(raw_velocity)
            velocity = sum(self.velocity_history) / len(self.velocity_history)

            if detect_palm_pause:
                pinching = self._is_pinching(pixel_lms)
                is_knife_stopped = self._update_knife_stop(pinching, velocity)
            else:
                self.knife_stop_active = False
                self.knife_enter_count = 0
                self.knife_exit_count = 0
                is_knife_stopped = False

            self.prev_x, self.prev_y = smooth_x, smooth_y

            cx, cy = int(smooth_x), int(smooth_y)
        else:
            self.missing_frames += 1
            if (
                self.missing_frames <= self.max_missing_frames
                and self.prev_x
                and self.prev_y
            ):
                # Hold the last point briefly to avoid abrupt dropouts near frame edges.
                cx, cy = int(self.prev_x), int(self.prev_y)
                velocity = 0.0
            else:
                self.knife_stop_active = False
                self.knife_enter_count = 0
                self.knife_exit_count = 0
                self.velocity_history.clear()

        self.prev_time = timestamp
        return cx, cy, velocity, is_knife_stopped
