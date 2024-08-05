import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QLineEdit, QLabel

class FrequencyCalculator(QWidget):
    def __init__(self):
        super().__init__()

        # Create the layout
        self.layout = QVBoxLayout()

        # Create the DAC frequency combobox
        self.dac_frequency_label = QLabel("Select DAC Frequency:")
        self.dac_frequency_combobox = QComboBox()
        self.dac_frequencies = [125e6, 112.5e6, 100e6, 87.5e6, 75e6, 62.5e6, 50e6, 37.5e6, 25e6, 12.5e6, 1e6]
        self.dac_frequency_combobox.addItems([f"{freq/1e6} MHz" for freq in self.dac_frequencies])

        # Create the DAC steps input
        self.dac_steps_label = QLabel("Enter DAC Steps:")
        self.dac_steps_input = QLineEdit()

        # Create the signal frequency combobox
        self.signal_frequency_label = QLabel("Possible Signal Frequencies:")
        self.signal_frequency_combobox = QComboBox()

        # Add widgets to the layout
        self.layout.addWidget(self.dac_frequency_label)
        self.layout.addWidget(self.dac_frequency_combobox)
        self.layout.addWidget(self.dac_steps_label)
        self.layout.addWidget(self.dac_steps_input)
        self.layout.addWidget(self.signal_frequency_label)
        self.layout.addWidget(self.signal_frequency_combobox)

        # Set the layout for the main window
        self.setLayout(self.layout)

        # Connect signals and slots
        self.dac_steps_input.returnPressed.connect(self.update_signal_frequencies)

        self.setWindowTitle("DAC Frequency Selector")

    def update_signal_frequencies(self):
        # Get the DAC steps
        try:
            dac_steps = int(self.dac_steps_input.text())
            if dac_steps <= 0:
                raise ValueError
        except ValueError:
            self.signal_frequency_combobox.clear()
            self.signal_frequency_combobox.addItem("Invalid Steps")
            return

        # Calculate possible signal frequencies for all DAC frequencies
        signal_frequencies = []
        for dac_frequency in self.dac_frequencies:
            signal_frequency = dac_frequency / dac_steps
            signal_frequencies.append(f"{signal_frequency/1e6:.6f} MHz")

        # Update the signal frequency combobox
        self.signal_frequency_combobox.clear()
        self.signal_frequency_combobox.addItems(signal_frequencies)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FrequencyCalculator()
    window.show()
    sys.exit(app.exec())
