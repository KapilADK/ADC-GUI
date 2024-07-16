import numpy as np
import matplotlib.pyplot as plt
import csv

# Initialize the measurement: Configure DAC and ADC
def init_measurement(frequency, amplitude):
    # DAC and ADC configuration logic here
    pass

# Acquire data from ADC
def acquire_data(duration, sampling_rate):
    # ADC data acquisition logic here
    return np.array([])  # Replace with actual data

# Calculate magnitude and phase
def calculate_magnitude_phase(input_signal, output_signal, sampling_rate):
    # Perform FFT on both signals
    fft_input = np.fft.fft(input_signal)
    fft_output = np.fft.fft(output_signal)

    # Find the frequency bin corresponding to the input frequency
    freq_bin = np.argmax(np.abs(fft_input))

    # Calculate magnitude and phase difference
    magnitude = np.abs(fft_output[freq_bin]) / np.abs(fft_input[freq_bin])
    phase = np.angle(fft_output[freq_bin]) - np.angle(fft_input[freq_bin])

    return magnitude, phase

# Sweep over the given frequency range
def frequency_sweep(start_freq, end_freq, step_freq, amplitude):
    frequencies = np.arange(start_freq, end_freq, step_freq)
    magnitudes = []
    phases = []

    for freq in frequencies:
        init_measurement(freq, amplitude)
        input_signal = acquire_data(duration=1, sampling_rate=1e6)  # Example parameters
        output_signal = acquire_data(duration=1, sampling_rate=1e6)  # Example parameters
        magnitude, phase = calculate_magnitude_phase(input_signal, output_signal, 1e6)
        magnitudes.append(magnitude)
        phases.append(phase)

    return frequencies, magnitudes, phases

# Plot Bode plot
def plot_bode(frequencies, magnitudes, phases):
    fig, ax1 = plt.subplots()

    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('Magnitude (dB)', color='tab:blue')
    ax1.semilogx(frequencies, 20 * np.log10(magnitudes), color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Phase (degrees)', color='tab:red')
    ax2.semilogx(frequencies, np.degrees(phases), color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    fig.tight_layout()
    plt.show()

# Save data to CSV
def save_data(frequencies, magnitudes, phases, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Frequency', 'Magnitude', 'Phase'])
        for f, m, p in zip(frequencies, magnitudes, phases):
            writer.writerow([f, m, p])

# Main function
def main():
    start_freq = 10
    end_freq = 10e6
    step_freq = 100e3
    amplitude = 1.0

    frequencies, magnitudes, phases = frequency_sweep(start_freq, end_freq, step_freq, amplitude)
    plot_bode(frequencies, magnitudes, phases)
    save_data(frequencies, magnitudes, phases, 'bode_plot_data.csv')

if __name__ == "__main__":
    main()
