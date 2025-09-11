import asyncio
import logging
from typing import Optional
import cv2
from mediapipe.python.solutions.hands import Hands, HAND_CONNECTIONS
from mediapipe.python.solutions.drawing_utils import draw_landmarks
import numpy as np
from pygame import mixer
from playground.piano import Piano
from config.config import CONFIG

# Configure logging
logger = logging.getLogger(__name__)


class VirtualPiano:
    """Main class for the virtual piano application."""

    def __init__(self):
        self.hands = None
        self.cap = None
        self.piano = None
        self.prev_positions = {}  # dict: idx -> (x, y, t)
        self.calibration_key = 0
        self.calibration_start_pos = None

    def setup(self) -> None:
        """Initialize pygame, MediaPipe, and camera."""
        try:
            mixer.init()
        except Exception as e:
            logger.error(f"Failed to initialize pygame mixer: {e}")
            raise

        try:
            self.hands = Hands(**CONFIG["hands_config"])
        except Exception as e:
            logger.error(f"Failed to initialize MediaPipe Hands: {e}")
            raise

        try:
            self.cap = cv2.VideoCapture(CONFIG["camera_index"])
            ret, frame = self.cap.read()
            if not ret:
                raise RuntimeError("Could not read from camera.")
            h, w = frame.shape[:2]
            self.piano = Piano((w, h))
        except Exception as e:
            logger.error(f"Failed to initialize camera or piano: {e}")
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
        else:
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
                    if hasattr(self.piano, "interact"):
                        self.piano.interact((x, y), vel)

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
        cv2.imshow("Virtual Piano", frame)

        # Check for keys
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            logger.info("Exit requested by user.")
            raise SystemExit
        elif key == ord("r"):
            logger.info("Reset requested by user.")
            # Implemente a ação de reset se necessário
            pass

    def handle_calibration(self, frame: np.ndarray, result: Optional[object]) -> None:
        """Handle key position calibration."""
        if self.calibration_key is None or self.calibration_key >= len(CONFIG["keys"]):
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
            # Corrigir cálculo do tamanho para evitar erro de indexação
            key_config["size"] = (50, 50)  # Valor padrão, ajuste conforme necessário
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
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        if self.hands:
            self.hands.close()
        mixer.quit()
        logger.info("Resources cleaned up.")
