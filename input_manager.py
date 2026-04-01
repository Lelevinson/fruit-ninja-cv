import pygame
import cv2
import math
import time
from sensors import HandTracker, WebcamStream  # Re-using existing robust sensors logic


class InputProvider:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def get_input(self):
        """
        Returns (x, y, velocity, is_paused)
        x, y: Screen coordinates (or None)
        velocity: Pixels per second
        is_paused: Boolean (e.g. open palm)
        """
        return None, None, 0, False

    def cleanup(self):
        pass


class MouseInput(InputProvider):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.prev_pos = None
        self.prev_time = time.time()

    def get_input(self):
        cur_time = time.time()
        dt = cur_time - self.prev_time
        if dt == 0:
            dt = 0.001

        mx, my = pygame.mouse.get_pos()
        buttons = pygame.mouse.get_pressed()

        # Only track "blade" if left click is held
        if not buttons[0]:
            self.prev_pos = None
            return None, None, 0, False

        velocity = 0
        if self.prev_pos:
            dist = math.hypot(mx - self.prev_pos[0], my - self.prev_pos[1])
            velocity = dist / dt

        self.prev_pos = (mx, my)
        self.prev_time = cur_time
        return mx, my, velocity, False  # Mouse can't really "pause" with gesture


class HandInput(InputProvider):
    def __init__(self, width, height):
        super().__init__(width, height)
        # Initialize Webcam and Tracker
        # We reuse the logic from sensors.py which is already threaded and optimized
        self.webcam = WebcamStream(src=0, width=width, height=height).start()
        self.tracker = HandTracker(detection_con=0.45, track_con=0.45)
        self.last_frame = None
        self._warned_no_frame = False

    def get_input(self):
        frame = self.webcam.read()
        if frame is None:
            if not self._warned_no_frame:
                print("[Camera] Waiting for frames from webcam...")
                self._warned_no_frame = True
            return None, None, 0, False

        if self._warned_no_frame:
            print("[Camera] Webcam feed recovered.")
            self._warned_no_frame = False

        # Flip for mirror effect
        frame = cv2.flip(frame, 1)
        self.last_frame = frame

        # Tracker returns raw frame coords (assuming sensors.py returns pixels)
        # sensors.py find_position signature: (frame) -> cx, cy, velocity, is_palm_open
        tx, ty, velocity, is_knife_stopped = self.tracker.find_position(
            frame, detect_palm_pause=True
        )

        # If sensors.py returns None, tx is None
        if tx is None:
            return None, None, 0, False

        # Map logic:
        # sensors.py already returns pixel coordinates relative to the frame passed in.
        # Since we flipped the frame, and passed it to find_position, the x,y are correct for the flipped frame.
        # Scale from live camera frame dimensions to screen dimensions.
        cam_h, cam_w = frame.shape[:2]
        if cam_w == 0 or cam_h == 0:
            return None, None, 0, False

        sx = int((tx / cam_w) * self.width)
        sy = int((ty / cam_h) * self.height)

        sx = max(0, min(self.width - 1, sx))
        sy = max(0, min(self.height - 1, sy))

        return sx, sy, velocity, is_knife_stopped

    def get_frame(self):
        """Optional: Return frame for drawing background"""
        frame = self.last_frame
        if frame is None:
            frame = self.webcam.read()  # Access last frame directly or via read()
        if frame is not None:
            if self.last_frame is None:
                frame = cv2.flip(frame, 1)
                self.last_frame = frame
        return frame

    def cleanup(self):
        self.last_frame = None
        self.webcam.stop()
