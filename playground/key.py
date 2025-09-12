import logging
from typing import Tuple
import cv2
import numpy as np
from pygame import mixer

from config.config import CONFIG

logger = logging.getLogger(__name__)


class Key:
    """Represents a single piano key with position, sound, and hit detection."""

    def __init__(
        self,
        name: str,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        sound_path: str,
        cooldown: float,
        key_type: str,
    ):
        self.name = name
        self.pos = pos
        self.size = size
        self.cooldown = cooldown
        self.key_type = key_type
        self.last_hit = 0.0
        try:
            self.sound = mixer.Sound(sound_path)
            self.sound.set_volume(CONFIG["volume"])
        except Exception as e:
            logger.error(f"Failed to load sound {sound_path}: {e}")
            raise

    def draw(self, frame: np.ndarray, current_time: float) -> None:
        """Draw the key on the frame, changing color if recently hit."""
        color = (
            (0, 255, 0)
            if current_time - self.last_hit < self.cooldown
            else (255, 255, 255)
            if self.key_type == "white"
            else (0, 0, 0)
        )
        top_left = self.pos
        bottom_right = (self.pos[0] + self.size[0], self.pos[1] + self.size[1])
        cv2.rectangle(
            frame, top_left, bottom_right, color, -1 if self.key_type == "black" else 4
        )
        cv2.putText(
            frame,
            self.name,
            (self.pos[0], self.pos[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

    def check_hit(
        self,
        hand_pos: Tuple[int, int],
        hand_vel: float,
        current_time: float,
        velocity_threshold: float,
    ) -> bool:
        """Check if the key is hit based on hand position and velocity."""
        x, y = hand_pos
        x0, y0 = self.pos
        w, h = self.size
        if x0 <= x <= x0 + w and y0 <= y <= y0 + h and hand_vel > velocity_threshold:
            if current_time - self.last_hit > self.cooldown:
                try:
                    self.sound.play()
                    self.last_hit = current_time
                    return True
                except Exception as e:
                    logger.error(f"Error playing sound for {self.name}: {e}")
                    return False
        return False
