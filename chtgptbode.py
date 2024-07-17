import numpy as np

# Parameters
dac_frequency = 12.5e6  # DAC output frequency (12.5 MHz)
adc_sampling_frequency = 125e6  # ADC sampling frequency (125 MHz)
samples_per_dac_period = int(adc_sampling_frequency / dac_frequency)
num_dac_samples = 2 * samples_per_dac_period  # Number of samples over 2 periods of DAC

# Simulate DAC output (sine wave) for 2 periods
time_dac = np.arange(num_dac_samples) / adc_sampling_frequency
dac_output = np.sin(2 * np.pi * dac_frequency * time_dac)

# Simulate corresponding ADC samples (with noise or some effect)
adc_samples = np.sin(2 * np.pi * dac_frequency * time_dac) + 0.01 * np.random.randn(num_dac_samples)

# Calculate the average of ADC samples for each DAC output over 2 periods
averages = []

# Loop through each DAC sample and compute the average of corresponding ADC samples over 2 periods
for i in range(samples_per_dac_period):
    dac_sample = dac_output[i]
    corresponding_adc_samples = adc_samples[i::samples_per_dac_period]  # Get ADC samples corresponding to this DAC output over 2 periods
    average_adc_value = np.mean(corresponding_adc_samples)
    averages.append(average_adc_value)

print("Averages of ADC samples for each DAC output over 2 periods:", averages)
