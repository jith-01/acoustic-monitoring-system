# Audio stream parameters
CHUNK = 1024
FORMAT = 'paInt16'
CHANNELS = 1
RATE = 44100
MAX_INT16 = 32768.0 

# Mode configurations
MODES = {
    "Low (40-70 dB)": {"min": 40, "max": 70, "threshold": 60},
    "Medium (71-100 dB)": {"min": 71, "max": 100, "threshold": 80},
    "High (101-130 dB)": {"min": 101, "max": 130, "threshold": 120}
}

# Plotting constants
FIXED_MAX = 8
MAGNITUDE_SCALING = 30

# Alert parameters
ALERT_COOLDOWN = 1
CALIBRATION_FACTOR = 80

# VAD parameters
VAD_THRESHOLD = 0.015
SPECTRAL_FLATNESS_THRESHOLD = 0.3
ALPHA = 0.95
SPEECH_FREQ_LOW = 85
SPEECH_FREQ_HIGH = 3000
VOICE_HOLD_COUNT = 5