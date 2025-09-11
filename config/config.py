CONFIG = {
    "hit_velocity_threshold": 1000,
    "key_cooldown": 0.3,
    "keys": [
        {
            "name": "C4",
            "pos": (0.2, 0.7),
            "size": (50, 100),
            "sound": "sounds/piano_c4.wav",
            "type": "white",
        },
        {
            "name": "C#4",
            "pos": (0.25, 0.65),
            "size": (30, 60),
            "sound": "sounds/piano_cs4(fake).wav",
            "type": "black",
        },
        {
            "name": "D4",
            "pos": (0.3, 0.7),
            "size": (50, 100),
            "sound": "sounds/piano_d4.wav",
            "type": "white",
        },
        {
            "name": "D#4",
            "pos": (0.35, 0.65),
            "size": (30, 60),
            "sound": "sounds/piano_ds4(fake).wav",
            "type": "black",
        },
        {
            "name": "E4",
            "pos": (0.4, 0.7),
            "size": (50, 100),
            "sound": "sounds/piano_e4.wav",
            "type": "white",
        },
        {
            "name": "F4",
            "pos": (0.5, 0.7),
            "size": (50, 100),
            "sound": "sounds/piano_f4.wav",
            "type": "white",
        },
        {
            "name": "G4",
            "pos": (0.6, 0.7),
            "size": (50, 100),
            "sound": "sounds/piano_g4.wav",
            "type": "white",
        },
    ],
    # Quando True, o app entra no modo de calibração (usar apenas durante ajuste).
    "calibration_mode": False,
    "camera_index": 0,
    "hands_config": {
        "max_num_hands": 2,
        "min_detection_confidence": 0.7,
        "min_tracking_confidence": 0.7,
    },
    "fps": 60,
}
