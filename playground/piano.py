from typing import Tuple, List
import numpy as np
import asyncio

from playground.key import Key
from config.config import CONFIG
from playground.recorder import Recorder


class Piano:
    """Manages a collection of piano keys."""

    def __init__(self, frame_dim: Tuple[int, int]):
        self.keys: List[Key] = []
        self.keys_dict = {}  # Dict for quick access by name
        w, h = frame_dim
        for key_config in CONFIG["keys"]:
            pos = (int(w * key_config["pos"][0]), int(h * key_config["pos"][1]))
            size = key_config["size"]
            key = Key(
                key_config["name"],
                pos,
                size,
                key_config["sound"],
                CONFIG["key_cooldown"],
                key_config["type"],
            )
            self.keys.append(key)
            self.keys_dict[key_config["name"]] = key

    def draw(self, frame: np.ndarray) -> None:
        """Draw all keys on the frame, white keys first, then black."""
        current_time = asyncio.get_event_loop().time()
        for key in self.keys:
            if key.key_type == "white":
                key.draw(frame, current_time)
        for key in self.keys:
            if key.key_type == "black":
                key.draw(frame, current_time)

    def interact(
        self, hand_pos: Tuple[int, int], hand_vel: float, recorder: "Recorder"
    ) -> None:
        """Check for interactions with all keys, prioritizing black keys."""
        current_time = asyncio.get_event_loop().time()
        hit = False
        # Check black keys first
        for key in self.keys:
            if key.key_type == "black" and key.check_hit(
                hand_pos, hand_vel, current_time, CONFIG["sensitivity"]
            ):
                recorder.record_note(key.name)
                hit = True
                break
        if not hit:
            for key in self.keys:
                if key.key_type == "white" and key.check_hit(
                    hand_pos, hand_vel, current_time, CONFIG["sensitivity"]
                ):
                    recorder.record_note(key.name)
                    break
