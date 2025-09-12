import asyncio
from typing import List, Tuple
import logging
from pygame import mixer

from config.config import CONFIG

logger = logging.getLogger(__name__)


class Recorder:
    """Manages recording and playback of note sequences."""

    def __init__(self):
        self.sequence: List[Tuple[str, float]] = []  # (note_name, timestamp)
        self.start_time: float = 0.0
        self.playback_task = None

    def start_recording(self) -> None:
        """Start recording sequence."""
        self.sequence.clear()
        self.start_time = asyncio.get_event_loop().time()
        CONFIG["recording_mode"] = True
        logger.info("Recording started.")

    def stop_recording(self) -> None:
        """Stop recording sequence."""
        CONFIG["recording_mode"] = False
        logger.info("Recording stopped.")

    def record_note(self, note_name: str) -> None:
        """Record a note with relative timestamp."""
        if CONFIG["recording_mode"]:
            current_time = asyncio.get_event_loop().time()
            relative_time = current_time - self.start_time
            self.sequence.append((note_name, relative_time))
            logger.debug(f"Recorded note: {note_name} at {relative_time}")

    async def playback(self, keys_dict: dict) -> None:
        """Playback the recorded sequence."""
        CONFIG["playback_mode"] = True
        if not mixer.get_init():
            mixer.init()
        start_time = asyncio.get_event_loop().time()
        last_time = start_time
        for note_name, rel_time in self.sequence:
            # Aguarda o tempo relativo entre notas, considerando o tempo desde o início
            wait_time = (start_time + rel_time) - last_time
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            last_time = start_time + rel_time
            if note_name in keys_dict:
                try:
                    keys_dict[note_name].sound.play()
                except Exception as e:
                    logger.error(f"Error playing back {note_name}: {e}")
        CONFIG["playback_mode"] = False
        logger.info("Playback completed.")

    def start_playback(self, keys_dict: dict) -> None:
        """Start async playback."""
        if self.sequence:
            self.playback_task = asyncio.create_task(self.playback(keys_dict))

    def stop_playback(self) -> None:
        """Stop playback if running."""
        if self.playback_task:
            self.playback_task.cancel()
            CONFIG["playback_mode"] = False
            logger.info("Playback stopped.")
