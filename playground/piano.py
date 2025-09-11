from typing import Tuple, List
import numpy as np
import asyncio

from playground.key import Key
from config.config import CONFIG


class Piano:
    """Manages a collection of piano keys."""

    def __init__(self, frame_dim: Tuple[int, int]):
        self.keys: List[Key] = []
        w, h = frame_dim
        for key_config in CONFIG["keys"]:
            pos = (int(w * key_config["pos"][0]), int(h * key_config["pos"][1]))
            size = key_config["size"]
            self.keys.append(
                Key(
                    key_config["name"],
                    pos,
                    size,
                    key_config["sound"],
                    CONFIG["key_cooldown"],
                    key_config["type"],
                )
            )

    def draw(self, frame: np.ndarray) -> None:
        """Draw all keys on the frame, white keys first, then black."""
        current_time = asyncio.get_event_loop().time()
        # Draw white keys first
        for key in self.keys:
            if key.key_type == "white":
                key.draw(frame, current_time)
        # Draw black keys on top
        for key in self.keys:
            if key.key_type == "black":
                key.draw(frame, current_time)

    def interact(self, hand_pos: Tuple[int, int], hand_vel: float) -> None:
        """Check for interactions with all keys, prioritizing black keys."""
        current_time = asyncio.get_event_loop().time()
        # Check black keys first (they overlap white keys)
        for key in self.keys:
            if key.key_type == "black" and key.check_hit(
                hand_pos, hand_vel, current_time, CONFIG["hit_velocity_threshold"]
            ):
                return
        # Check white keys
        for key in self.keys:
            if key.key_type == "white" and key.check_hit(
                hand_pos, hand_vel, current_time, CONFIG["hit_velocity_threshold"]
            ):
                return
