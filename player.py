import numpy as np
import sounddevice as sd
import time


class SineWavePlayer:
    def __init__(self, frequency, sample_rate=44100):
        self.frequency = [frequency * (i + 1) for i in range(1)]
        self.sample_rate = sample_rate
        self.time = 0
        self.amplitude = 0.2
        self.target_frequency = self.frequency[:]
        self.playing = False
        self.number_harmonics = len(self.frequency)
        self.update_counter = 0
        self.update_interval = 10  # Zmieniaj co 10 bloków

    def callback(self, outdata, frames, time, status):
        if status:
            print(f"Stan: {status}")
        if self.playing:
            t = np.linspace(
                self.time, self.time + frames / self.sample_rate, frames, endpoint=False
            )
            # Synchronizacja częstotliwości co 10 bloków
            if self.update_counter % self.update_interval == 0:
                self.frequency = self.target_frequency[:]
            self.update_counter += 1

            signal = sum(
                self.amplitude * np.sin(2 * np.pi * f * t).reshape(-1, 1)
                for f in self.frequency
            ) / (self.number_harmonics * 2)
            outdata[:] = signal
            self.time += frames / self.sample_rate
        else:
            return

    def set_freq(self, freq):
        self.target_frequency = [freq * (i + 1) for i in range(1)]

    def start(self):
        self.playing = True
        with sd.OutputStream(
            callback=self.callback,
            channels=1,
            samplerate=self.sample_rate,
            blocksize=4096, 
        ):
            while self.playing:
                time.sleep(0.01)

    def stop(self):
        self.playing = False

    def set_amplitude(self, amp):
        self.amplitude = amp
