import asyncio
import logging
import threading
from typing import Optional, Dict, Tuple
import cv2
import numpy as np
from pygame import mixer
from mediapipe.python.solutions.hands import Hands, HAND_CONNECTIONS
from mediapipe.python.solutions.drawing_utils import draw_landmarks
from playground.piano import Piano
from playground.recorder import Recorder
from playground.settings import SettingsMenu
from config.config import CONFIG

# Configure logging
logger = logging.getLogger(__name__)


class VirtualPiano:
    """Main class for the virtual piano application."""

    def __init__(self):
        self.hands: Optional[Hands] = None
        self.cap: Optional[cv2.VideoCapture] = None
        self.piano: Optional[Piano] = None
        self.recorder: Optional[Recorder] = None
        self.settings: Optional[SettingsMenu] = None
        self.prev_positions: Dict[int, Tuple[int, int, float]] = {}
        self.calibration_key: int = 0
        self.calibration_start_pos: Optional[Tuple[int, int]] = None

    def setup(self) -> None:
        """Initialize pygame, MediaPipe, camera, recorder, and settings."""
        try:
            mixer.init()
            mixer.music.set_volume(CONFIG["volume"])
        except Exception as e:
            logger.error(f"Failed to initialize pygame mixer: {e}")
            raise

        try:
            self.hands = Hands(**CONFIG["hands_config"])
        except Exception as e:
            logger.error(f"Failed to initialize MediaPipe Hands: {e}")
            raise

        try:
            from playground.recorder import Recorder
            from playground.settings import SettingsMenu

            self.recorder = Recorder()
            self.settings = SettingsMenu()
            self.cap = cv2.VideoCapture(CONFIG["camera_index"])
            ret, frame = self.cap.read()
            if not ret:
                raise RuntimeError("Could not read from camera.")
            h, w = frame.shape[:2]
            self.piano = Piano((w, h))
        except Exception as e:
            logger.error(
                f"Failed to initialize camera, piano, recorder, or settings: {e}"
            )
            raise

    def update_loop(self) -> None:
        """Process one frame of the video feed."""
        if not self.cap or not self.cap.isOpened() or not self.hands or not self.piano:
            logger.error("Camera, hands, or piano not initialized or closed.")
            return

        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to read frame from camera.")
            return

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)

        w, h = frame.shape[1], frame.shape[0]

        if CONFIG["calibration_mode"]:
            self.handle_calibration(frame, result)
        elif not CONFIG["playback_mode"]:  # Disable interactions during playback
            multi_hand_landmarks = getattr(result, "multi_hand_landmarks", None)
            if multi_hand_landmarks:
                for idx, hand_landmarks in enumerate(multi_hand_landmarks):
                    lm = hand_landmarks.landmark[8]  # Index finger tip
                    x, y = int(lm.x * w), int(lm.y * h)
                    t = asyncio.get_event_loop().time()
                    # Compute vertical velocity
                    vel = 0.0
                    if idx in self.prev_positions:
                        _, py, pt = self.prev_positions[idx]
                        dt = t - pt
                        vel = (y - py) / dt if dt > 0 else 0.0
                    self.prev_positions[idx] = (x, y, t)

                    # Process interaction for this hand
                    if hasattr(self.piano, "interact") and self.recorder:
                        self.piano.interact((x, y), vel, self.recorder)

                    # Draw hand landmarks
                    draw_landmarks(frame, hand_landmarks, list(HAND_CONNECTIONS))

        if hasattr(self.piano, "draw"):
            self.piano.draw(frame)
        if CONFIG["calibration_mode"]:
            cv2.putText(
                frame,
                "Calibration Mode: Press 'c' to confirm, 'n' for next key",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )
        if CONFIG["recording_mode"]:
            cv2.putText(
                frame,
                "Recording...",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 0, 0),
                2,
            )
        if CONFIG["playback_mode"]:
            cv2.putText(
                frame,
                "Playing back...",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )
        cv2.imshow("Virtual Piano", frame)

        # Check for keys
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            logger.info("Exit requested by user.")
            raise SystemExit
        elif key == ord("r"):
            CONFIG["calibration_mode"] = True
            self.calibration_key = 0
            logger.info("Calibration mode activated.")
        elif key == ord("g"):
            if self.recorder:
                if CONFIG["recording_mode"]:
                    self.recorder.stop_recording()
                else:
                    self.recorder.start_recording()
        elif key == ord("p"):
            if self.recorder:
                if CONFIG["playback_mode"]:
                    self.recorder.stop_playback()
                else:
                    self.recorder.start_playback(self.piano.keys_dict)
        elif key == ord("s"):
            if self.settings:
                settings_thread = threading.Thread(target=self.run_settings_menu)
                settings_thread.start()

    def run_settings_menu(self) -> None:
        """Executa o menu de configurações em uma thread separada."""
        if self.settings:
            self.settings.init()
            while self.settings.run():
                pass
            self.settings.cleanup()

    def handle_calibration(self, frame: np.ndarray, result: Optional[object]) -> None:
        """Handle key position calibration."""
        if self.calibration_key is None or self.calibration_key >= len(CONFIG["keys"]):
            CONFIG["calibration_mode"] = False
            logger.info("Calibration completed or no keys to calibrate.")
            return

        w, h = frame.shape[1], frame.shape[0]
        key_config = CONFIG["keys"][self.calibration_key]
        cv2.putText(
            frame,
            f"Calibrating {key_config['name']}: Move hand to top-left corner",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

        multi_hand_landmarks = getattr(result, "multi_hand_landmarks", None)
        if multi_hand_landmarks:
            hand_landmarks = multi_hand_landmarks[0]
            lm = hand_landmarks.landmark[8]  # Index finger tip
            x, y = int(lm.x * w), int(lm.y * h)

            if self.calibration_start_pos is None:
                self.calibration_start_pos = (x, y)
            else:
                cv2.rectangle(frame, self.calibration_start_pos, (x, y), (0, 255, 0), 2)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("c") and self.calibration_start_pos is not None:
            x, y = self.calibration_start_pos
            key_config["pos"] = (x / w, y / h)
            # Update size based on rectangle drawn
            curr_x, curr_y = x, y
            if multi_hand_landmarks:
                lm = multi_hand_landmarks[0].landmark[8]
                curr_x, curr_y = int(lm.x * w), int(lm.y * h)
            key_config["size"] = (abs(curr_x - x), abs(curr_y - y))
            self.calibration_key += 1
            self.calibration_start_pos = None
            if self.calibration_key >= len(CONFIG["keys"]):
                CONFIG["calibration_mode"] = False
                logger.info("Calibration completed.")
        elif key == ord("n"):
            self.calibration_key += 1
            self.calibration_start_pos = None
            if self.calibration_key >= len(CONFIG["keys"]):
                CONFIG["calibration_mode"] = False
                logger.info("Calibration completed.")

    def cleanup(self) -> None:
        """Release resources."""
        if self.recorder:
            self.recorder.stop_playback()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        if self.hands:
            self.hands.close()
        mixer.quit()
        logger.info("Resources cleaned up.")
