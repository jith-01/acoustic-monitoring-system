import numpy as np
from config import *

class VoiceActivityDetector:
    def __init__(self):
        self.noise_energy = 0.0
        self.voice_buffer = np.zeros(8, dtype=bool)
        self.voice_detected = False
        self.voice_hold_counter = 0
        self.sf_history = np.zeros(5)
        self.energy_ratio_history = np.zeros(5)
        self.x_fft = np.linspace(0, RATE / 2, CHUNK // 2 + 1)

    def calculate_spectral_flatness(self, fft_data):
        speech_range = np.logical_and(self.x_fft >= SPEECH_FREQ_LOW, 
                                    self.x_fft <= SPEECH_FREQ_HIGH) 
        speech_fft = fft_data[speech_range] + 1e-10
        geometric_mean = np.exp(np.mean(np.log(speech_fft)))
        arithmetic_mean = np.mean(speech_fft)
        return geometric_mean / arithmetic_mean

    def calculate_energy_ratio(self, fft_data):
        speech_mask = np.logical_and(self.x_fft >= 300, self.x_fft <= 3000)
        total_energy = np.sum(fft_data ** 2)
        speech_energy = np.sum(fft_data[speech_mask] ** 2)
        return speech_energy / total_energy if total_energy > 1e-10 else 0

    def detect_voice(self, audio_data, fft_data):
        energy = np.mean(np.square(audio_data, dtype=np.float32)) / (MAX_INT16 ** 2)
        spectral_flatness = self.calculate_spectral_flatness(fft_data)
        energy_ratio = self.calculate_energy_ratio(fft_data)

        # Update histories
        self.sf_history[:-1] = self.sf_history[1:]
        self.sf_history[-1] = spectral_flatness
        smoothed_sf = np.mean(self.sf_history)

        self.energy_ratio_history[:-1] = self.energy_ratio_history[1:]
        self.energy_ratio_history[-1] = energy_ratio
        smoothed_energy_ratio = np.mean(self.energy_ratio_history)

        # Update noise energy
        if energy < VAD_THRESHOLD * 0.5:
            self.noise_energy = ALPHA * self.noise_energy + (1 - ALPHA) * energy
        else:
            self.noise_energy = max(self.noise_energy, 1e-6)

        # Voice detection
        energy_detection = energy > (self.noise_energy * 2.5)
        flatness_detection = smoothed_sf < SPECTRAL_FLATNESS_THRESHOLD
        ratio_detection = smoothed_energy_ratio > 0.4

        current_frame_has_voice = energy_detection and (flatness_detection or ratio_detection)
        
        self.voice_buffer[:-1] = self.voice_buffer[1:]
        self.voice_buffer[-1] = current_frame_has_voice

        if np.mean(self.voice_buffer) > 0.4:
            self.voice_detected = True
            self.voice_hold_counter = VOICE_HOLD_COUNT
        elif self.voice_hold_counter > 0:
            self.voice_hold_counter -= 1
        else:
            self.voice_detected = False

        return self.voice_detected, smoothed_sf, energy, energy_ratio