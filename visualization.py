import matplotlib.pyplot as plt
import numpy as np  # Added missing import
from matplotlib.widgets import RadioButtons
from config import *

class Visualizer:
    def __init__(self, mode_changed_callback):
        self.fig = plt.figure(figsize=(12, 12))
        gs = self.fig.add_gridspec(4, 4)
        
        self.ax = self.fig.add_subplot(gs[0, :])
        self.ax1 = self.fig.add_subplot(gs[1:3, :])
        self.ax_db = self.fig.add_subplot(gs[3, :3])
        self.ax_radio = self.fig.add_subplot(gs[3, 3])

        # Initialize plots
        self.line, = self.ax.plot(np.arange(CHUNK), np.zeros(CHUNK, dtype=np.int16), 'r')
        self.line_fft, = self.ax1.semilogx(np.linspace(0, RATE / 2, CHUNK // 2 + 1), 
                                         np.zeros(CHUNK // 2 + 1), 'b')
        self.db_bar = self.ax_db.bar([0], [0], width=0.5, color='g')
        self.db_threshold_line = self.ax_db.axhline(y=MODES["Medium (71-100 dB)"]["threshold"], 
                                                  color='r', linestyle='-', linewidth=2)

        # Labels and indicators
        self.vad_label = self.ax_db.text(0.05, 0.9, "No Voice", transform=self.ax_db.transAxes,
                                       fontsize=10, color='black', bbox=dict(facecolor='white', alpha=0.8))
        self.alert_indicator = self.ax_db.text(0.5, 0.5, "ALERT!", transform=self.ax_db.transAxes,
                                             fontsize=24, color='black', weight='bold', alpha=0.0,
                                             ha='center', va='center')
        # Axis settings
        self.setup_axes()
        self.setup_radio(mode_changed_callback)

    def setup_axes(self):
        self.ax.set_ylim(-32000, 32000)
        self.ax.set_xlim(0, CHUNK)
        self.ax.set_title("Waveform")
        self.ax.set_ylabel("Amplitude")

        self.ax1.set_xlim(20, RATE / 2)
        self.ax1.set_ylim(0, FIXED_MAX)
        self.ax1.set_title("Frequency Spectrum")
        #self.ax1.set_xlabel("Frequency (Hz)")
        self.ax1.set_ylabel("Magnitude")

        current_mode = "Low (40-70 dB)"
        self.ax_db.set_xlim(-0.5, 0.5)
        self.ax_db.set_ylim(MODES[current_mode]["min"], MODES[current_mode]["max"])
        self.ax_db.set_title(f"Sound Level (dB SPL) - {current_mode} - Alert at {MODES[current_mode]['threshold']} dB")
        self.ax_db.set_ylabel("dB")
        self.ax_db.set_xticks([])

    def setup_radio(self, callback):
        self.ax_radio.set_title("Select Mode")
        self.radio = RadioButtons(self.ax_radio, list(MODES.keys()))
        self.radio.on_clicked(callback)
        plt.tight_layout()

    def update_mode(self, label):
        self.ax_db.set_ylim(MODES[label]["min"], MODES[label]["max"])
        self.ax_db.set_title(f"Sound Level (dB SPL) - {label} - Alert at {MODES[label]['threshold']} dB")
        self.db_threshold_line.remove()
        self.db_threshold_line = self.ax_db.axhline(y=MODES[label]["threshold"], 
                                                  color='r', linestyle='-', linewidth=2)