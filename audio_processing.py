import numpy as np
import pyaudio as pa
from config import *

class AudioProcessor:
    def __init__(self):
        self.p = pa.PyAudio()
        self.stream = self.p.open(
            format=getattr(pa, FORMAT),
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        self.x = np.arange(CHUNK)
        self.x_fft = np.linspace(0, RATE / 2, CHUNK // 2 + 1)

    def read_audio(self):
        data = self.stream.read(CHUNK, exception_on_overflow=False)
        return np.frombuffer(data, dtype=np.int16)

    def calculate_db(self, audio_data):
        rms = np.sqrt(np.mean(np.square(audio_data, dtype=np.float32)))
        db_fs = 20 * np.log10(rms / MAX_INT16 + 1e-10) if rms > 0 else -96  # spl = 20*(log10(p/p0)); p= rms sound pressure in pascals; p0 = ref sound pressure 20 pa
        return max(0, db_fs + CALIBRATION_FACTOR)

    def calculate_fft(self, audio_data):
        return np.abs(np.fft.rfft(audio_data)) * MAGNITUDE_SCALING / (CHUNK * 32768)

    def cleanup(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()