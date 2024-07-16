import numpy as np
import matplotlib.pyplot as plt


def calculate_bode_at_f(input_signal, output_signal, f_input, fs):
    """
    Calculate the magnitude and phase at frequency f_input given input and output signals without FFT.

    :param input_signal: Array of input signal values.
    :param output_signal: Array of output signal values.
    :param f_input: Frequency at which to perform the calculation (Hz).
    :param fs: Sampling frequency (Hz).

    :return: Magnitude and Phase (in degrees) at frequency f_input.
    """
    # Length of the signal
    n = len(input_signal)

    # Generate reference sinusoids at frequency f_input
    t = np.arange(n) / fs
    ref_sin = np.sin(2 * np.pi * f_input * t)
    ref_cos = np.cos(2 * np.pi * f_input * t)

    # Compute dot products for input signal
    input_sin_dot = np.dot(input_signal, ref_sin)
    input_cos_dot = np.dot(input_signal, ref_cos)

    # Compute dot products for output signal
    output_sin_dot = np.dot(output_signal, ref_sin)
    output_cos_dot = np.dot(output_signal, ref_cos)

    # Calculate magnitudes and phases for input and output signals
    input_magnitude = np.sqrt(input_sin_dot**2 + input_cos_dot**2)
    output_magnitude = np.sqrt(output_sin_dot**2 + output_cos_dot**2)

    input_phase = np.arctan2(input_sin_dot, input_cos_dot)
    output_phase = np.arctan2(output_sin_dot, output_cos_dot)

    # Calculate the transfer function H(f_input)
    H_magnitude = output_magnitude / input_magnitude
    H_phase = np.degrees(output_phase - input_phase)

    return H_magnitude, H_phase


# Parameters
fs = 10e6  # Sampling frequency in Hz
frequencies = np.arange(
    1e3, 1e6 + 1, 1e3
)  # Frequencies from 1 kHz to 1 MHz in 1 kHz steps
duration = 0.01  # Duration of the signal in seconds

f_c = 10e3  # Cutoff frequency for the low-pass filter phase shift

# Arrays to store results
magnitudes = []
phases = []

# Loop over each frequency
for f_input in frequencies:
    t = np.arange(0, duration, 1 / fs)  # Time array
    input_signal = np.sin(2 * np.pi * f_input * t)  # Example input signal

    # Simulated output signal with decreasing amplitude above 10 kHz
    if f_input > f_c:
        attenuation_factor = f_c / f_input
    else:
        attenuation_factor = 1.0

    # Simulated phase shift in the style of a low-pass filter
    phase_shift = -np.arctan(f_input / f_c)
    output_signal = (
        0.5 * attenuation_factor * np.sin(2 * np.pi * f_input * t + phase_shift)
    )

    magnitude, phase = calculate_bode_at_f(input_signal, output_signal, f_input, fs)
    magnitudes.append(magnitude)
    phases.append(phase)


# Convert results to numpy arrays
magnitudes = np.array(magnitudes)
phases = np.array(phases)

# Plotting
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Magnitude plot
ax1.semilogx(frequencies, 20 * np.log10(magnitudes))
ax1.set_title("Bode Plot")
ax1.set_ylabel("Magnitude (dB)")
ax1.grid(True, which="both", ls="--")

# Phase plot
ax2.semilogx(frequencies, phases)
ax2.set_ylabel("Phase (degrees)")
ax2.set_xlabel("Frequency (Hz)")
ax2.grid(True, which="both", ls="--")

plt.show()
