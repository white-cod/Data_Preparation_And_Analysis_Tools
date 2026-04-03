import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy.signal import butter, filtfilt

class HarmonicApp:
    def __init__(self):
        self.init_amp = 1.0
        self.init_freq = 1.0
        self.init_phase = 0.0
        
        self.init_noise_mean = 0.0
        self.init_noise_cov = 0.1
        
        self.init_cutoff = 5.0
        
        self.show_noise_flag = True
        self.show_filtered_flag = True

        self.fs = 1000
        self.t = np.linspace(0, 10, self.fs * 10)
        
        self.base_noise = np.random.normal(0, 1, len(self.t))

        self.setup_ui()

    def harmonic_with_noise(self, amplitude, frequency, phase, noise_mean, noise_covariance, show_noise):
        clean_harmonic = amplitude * np.sin(2 * np.pi * frequency * self.t + phase)
        
        if show_noise:
            current_noise = self.base_noise * np.sqrt(noise_covariance) + noise_mean
            return clean_harmonic + current_noise
        else:
            return clean_harmonic

    def apply_filter(self, data, cutoff):
        nyq = 0.5 * self.fs
        normal_cutoff = cutoff / nyq
        
        if normal_cutoff <= 0 or normal_cutoff >= 1:
            return data
            
        b, a = butter(3, normal_cutoff, btype='low', analog=False)
        return filtfilt(b, a, data)

    def setup_ui(self):
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        plt.subplots_adjust(left=0.1, bottom=0.45, right=0.8)

        self.ax.set_title("Гармоніка з накладеним шумом та фільтрацією")
        self.ax.set_xlabel("Час (t)")
        self.ax.set_ylabel("Амплітуда (y)")
        self.ax.grid(True)

        self.line_harmonic, = self.ax.plot(self.t, np.zeros_like(self.t), lw=2, color='blue', label='Чиста гармоніка')
        self.line_noisy, = self.ax.plot(self.t, np.zeros_like(self.t), lw=1, color='red', alpha=0.5, label='Зашумлена гармоніка')
        self.line_filtered, = self.ax.plot(self.t, np.zeros_like(self.t), lw=2, color='green', label='Відфільтрована')
        self.ax.legend(loc='upper right')

        axcolor = 'lightgoldenrodyellow'
        
        ax_amp = plt.axes([0.15, 0.35, 0.55, 0.03], facecolor=axcolor)
        ax_freq = plt.axes([0.15, 0.30, 0.55, 0.03], facecolor=axcolor)
        ax_phase = plt.axes([0.15, 0.25, 0.55, 0.03], facecolor=axcolor)
        ax_noise_mean = plt.axes([0.15, 0.20, 0.55, 0.03], facecolor='mistyrose')
        ax_noise_cov = plt.axes([0.15, 0.15, 0.55, 0.03], facecolor='mistyrose')
        ax_cutoff = plt.axes([0.15, 0.10, 0.55, 0.03], facecolor='honeydew')

        self.s_amp = Slider(ax_amp, 'Amplitude', 0.1, 5.0, valinit=self.init_amp)
        self.s_freq = Slider(ax_freq, 'Frequency', 0.1, 10.0, valinit=self.init_freq)
        self.s_phase = Slider(ax_phase, 'Phase', 0.0, 2*np.pi, valinit=self.init_phase)
        self.s_noise_mean = Slider(ax_noise_mean, 'Noise Mean', -2.0, 2.0, valinit=self.init_noise_mean)
        self.s_noise_cov = Slider(ax_noise_cov, 'Noise Cov (Var)', 0.0, 2.0, valinit=self.init_noise_cov)
        self.s_cutoff = Slider(ax_cutoff, 'Filter Cutoff', 0.1, 50.0, valinit=self.init_cutoff)

        ax_check = plt.axes([0.75, 0.25, 0.15, 0.15])
        self.check = CheckButtons(ax_check, ['Show Noise', 'Show Filtered'], [self.show_noise_flag, self.show_filtered_flag])

        ax_reset = plt.axes([0.8, 0.05, 0.1, 0.04])
        self.b_reset = Button(ax_reset, 'Reset', color='lightblue', hovercolor='0.975')

        self.s_amp.on_changed(self.update)
        self.s_freq.on_changed(self.update)
        self.s_phase.on_changed(self.update)
        self.s_noise_mean.on_changed(self.update)
        self.s_noise_cov.on_changed(self.update)
        self.s_cutoff.on_changed(self.update)
        self.check.on_clicked(self.toggle_visibility)
        self.b_reset.on_clicked(self.reset)

        self.update(None)
        plt.show()

    def update(self, val):
        amp = self.s_amp.val
        freq = self.s_freq.val
        phase = self.s_phase.val
        n_mean = self.s_noise_mean.val
        n_cov = self.s_noise_cov.val
        cutoff = self.s_cutoff.val

        clean_y = self.harmonic_with_noise(amp, freq, phase, n_mean, n_cov, show_noise=False)
        self.line_harmonic.set_ydata(clean_y)

        noisy_y = self.harmonic_with_noise(amp, freq, phase, n_mean, n_cov, show_noise=True)
        
        if self.show_noise_flag:
            self.line_noisy.set_ydata(noisy_y)
            self.line_noisy.set_visible(True)
            signal_to_filter = noisy_y
        else:
            self.line_noisy.set_visible(False)
            signal_to_filter = clean_y

        filtered_y = self.apply_filter(signal_to_filter, cutoff)

        if self.show_filtered_flag:
            self.line_filtered.set_ydata(filtered_y)
            self.line_filtered.set_visible(True)
        else:
            self.line_filtered.set_visible(False)

        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw_idle()

    def toggle_visibility(self, label):
        if label == 'Show Noise':
            self.show_noise_flag = not self.show_noise_flag
        elif label == 'Show Filtered':
            self.show_filtered_flag = not self.show_filtered_flag
        self.update(None)

    def reset(self, event):
        self.s_amp.reset()
        self.s_freq.reset()
        self.s_phase.reset()
        self.s_noise_mean.reset()
        self.s_noise_cov.reset()
        self.s_cutoff.reset()
        
        if not self.show_noise_flag:
            self.check.set_active(0)
        if not self.show_filtered_flag:
            self.check.set_active(1)

if __name__ == '__main__':
    app = HarmonicApp()