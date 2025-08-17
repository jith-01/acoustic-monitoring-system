import time
import numpy as np
import matplotlib.pyplot as plt
from audio_processing import AudioProcessor
from visualization import Visualizer
from vad import VoiceActivityDetector
from config import *

def main():
    plt.ion() #interactive mode for matplotlib
    audio = AudioProcessor()
    vad = VoiceActivityDetector()
    
    def mode_changed(label):
        visualizer.update_mode(label)

    visualizer = Visualizer(mode_changed)
    db_history = np.zeros(5, dtype=np.float32)
    
    # Calibration
    print("Calibrating background noise... please remain silent for 3 seconds")
    calibration_frames = []
    for _ in range(30):
        data = audio.read_audio()
        energy = np.mean(np.square(data, dtype=np.float32)) / (MAX_INT16 ** 2)
        calibration_frames.append(energy)
        time.sleep(0.01)
    vad.noise_energy = np.mean(calibration_frames)
    print(f"Calibration complete. Background noise level: {vad.noise_energy:.6f}")

    last_alert_time = 0
    alert_active = False
    alert_fade = 0.0

    while True:
        try:
            data_int = audio.read_audio()
            fft_data = audio.calculate_fft(data_int)
            db_level = audio.calculate_db(data_int)

            # Update plots
            visualizer.line.set_ydata(data_int)
            visualizer.line_fft.set_ydata(fft_data)
            
            db_history[:-1] = db_history[1:]
            db_history[-1] = db_level
            avg_db = np.mean(db_history)
            
            visualizer.db_bar[0].set_height(avg_db)
            visualizer.db_bar[0].set_color('g' if avg_db < (MODES[visualizer.radio.value_selected]["threshold"] - 10) else
                                         'y' if avg_db < MODES[visualizer.radio.value_selected]["threshold"] else 'r')

            # Voice detection
            is_voice, sf, energy, energy_ratio = vad.detect_voice(data_int, fft_data)
            visualizer.vad_label.set_text("Voice Detected" if is_voice else "No Voice")
            visualizer.vad_label.set_color('green' if is_voice else 'black')

            # Alert handling
            current_time = time.time()
            if not is_voice and avg_db >= MODES[visualizer.radio.value_selected]["threshold"] and (current_time - last_alert_time) > ALERT_COOLDOWN:
                last_alert_time = current_time
                alert_active = True
                alert_fade = 1.0
                print(f"Alert! Non-voice sound level: {avg_db:.1f} dB exceeded threshold of {MODES[visualizer.radio.value_selected]['threshold']} dB")

            if alert_active:
                if alert_fade > 0:
                    visualizer.alert_indicator.set_alpha(alert_fade)
                    alert_fade -= 0.02
                else:
                    alert_active = False
                    visualizer.alert_indicator.set_alpha(0)

            plt.pause(0.001)

        except KeyboardInterrupt:
            print("Stopped by user")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

    audio.cleanup()
    plt.ioff()
    plt.close()

if __name__ == "__main__":
    main()