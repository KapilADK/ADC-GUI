from PyQt6.QtWidgets import (
    QPushButton,
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QGroupBox,
    QLineEdit,
    QLabel,
    QRadioButton,
)
from PyQt6.QtGui import QIntValidator
from PyQt6.QtCore import pyqtSlot
import sys

class DacBramSettingsTab(QGroupBox):
    def __init__(self):
        super().__init__()

        # default object variables for config:
        self.dwell_time_ms = "8e-06"
        self.dac_steps = 1000
        self.signal_type = "Sine"
        self.start_V = 0
        self.stop_V = 1
        self.amplitude = 1

        self.updating = False  # Flag to prevent recursion

        self.setupUI()
        self.update_frequency_options()

        # Signal slot connections
        self.dac_steps_edit.textChanged.connect(self.validate_dac_steps)
        self.dac_sample_rate_button.clicked.connect(self.update_dac_config)
        self.signal_frequency_button.clicked.connect(self.update_dac_config)
        self.dac_sample_rate_combobox.currentIndexChanged.connect(self.update_dac_config)
        self.dac_steps_edit.returnPressed.connect(self.update_dac_config)
        self.signal_frequency_combobox.currentIndexChanged.connect(self.get_frequency_info)

    def setupUI(self):
        self.port_layout = QHBoxLayout()
        self.setLayout(self.port_layout)

        # Add frequency group box to set sample rate of DAC and frequency of signal
        self.frequency_box = QGroupBox("Frequency setter")
        self.frequency_box_layout = QVBoxLayout()
        self.frequency_box.setLayout(self.frequency_box_layout)

        self.dac_sample_rate_layout = QHBoxLayout()
        self.dac_sample_rate_button = QRadioButton("DAC Sample rate")
        self.dac_sample_rate_button.setChecked(True)

        self.dac_sample_rate_combobox = QComboBox()
        self.dac_sample_rates = [
            125, 62.5, 31.25, 25, 15.625, 12.5, 7.8125, 6.25, 5, 3.90625,
            3.125, 2.5, 1.25, 1, 0.625, 0.5
        ]
        for dac_sample_rate in self.dac_sample_rates:
            self.dac_sample_rate_combobox.addItem(f"{dac_sample_rate} MHz")
        self.dac_steps_label = QLabel("DAC Steps")
        self.dac_steps_edit = QLineEdit()
        self.dac_steps_edit.setValidator(QIntValidator())
        self.dac_steps_edit.setText(str(self.dac_steps))
        self.dwell_time_ms_label = QLabel("Dwell time(ms):")
        self.show_dwell_time_ms_label = QLabel()
        self.show_dwell_time_ms_label.setText(str(self.dwell_time_ms))
        self.dwell_time_ms_list = [0.000008, 0.000016, 0.000032, 0.00004, 0.000034, 0.00008, 0.000128, 0.00016, 0.0002, 0.000256, 0.00032, 0.0004, 0.0008, 0.001, 0.0016, 0.002]

        self.dac_sample_rate_layout.addWidget(self.dac_sample_rate_button)
        self.dac_sample_rate_layout.addWidget(self.dac_sample_rate_combobox)
        self.dac_sample_rate_layout.addWidget(self.dac_steps_label)
        self.dac_sample_rate_layout.addWidget(self.dac_steps_edit)
        self.dac_sample_rate_layout.addWidget(self.dwell_time_ms_label)
        self.dac_sample_rate_layout.addWidget(self.show_dwell_time_ms_label)

        self.signal_frequency_layout = QHBoxLayout()
        self.signal_frequency_button = QRadioButton("Signal Frequency")
        self.signal_frequency_combobox = QComboBox()

        self.max_dac_steps_label = QLabel(f"Max. DAC steps:\t16000")

        self.signal_frequency_layout.addWidget(self.signal_frequency_button)
        self.signal_frequency_layout.addWidget(self.signal_frequency_combobox)
        self.signal_frequency_layout.addWidget(self.max_dac_steps_label)

        self.frequency_box_layout.addLayout(self.dac_sample_rate_layout)
        self.frequency_box_layout.addLayout(self.signal_frequency_layout)

        # Add each box/layout to the Port layout
        self.port_layout.addWidget(self.frequency_box)

    def update_frequency_options(self):
        if self.dac_sample_rate_button.isChecked():
            self.dac_sample_rate_combobox.setVisible(True)
            self.signal_frequency_combobox.setVisible(False)
        else:
            self.dac_sample_rate_combobox.setVisible(False)
            self.signal_frequency_combobox.setVisible(True)

    def validate_dac_steps(self, text):
        if text and int(text) > 16000:
            # Revert the input to the previous valid state
            cursor_position = self.dac_steps_edit.cursorPosition()
            self.dac_steps_edit.setText(text[:-1])
            self.dac_steps_edit.setCursorPosition(cursor_position - 1)

    def get_frequency_info(self):
        if self.dac_sample_rate_button.isChecked():
            index = self.dac_sample_rate_combobox.currentIndex()
            
        else:
            index = self.signal_frequency_combobox.currentIndex()

        self.dwell_time_ms = self.dwell_time_ms_list[index]
        self.show_dwell_time_ms_label.setText(str(self.dwell_time_ms))

    def show_signal_frequency(self):
        if self.signal_frequency_button.isChecked():
            self.signal_frequency_combobox.clear()
            self.dac_steps = int(self.dac_steps_edit.text())
            signal_frequencies = []
            for dac_sample_rate in self.dac_sample_rates:
                signal_frequency = float(dac_sample_rate * 1e6) / self.dac_steps
                signal_frequencies.append(f"{signal_frequency:.2f} Hz")
            for frequency in signal_frequencies:
                self.signal_frequency_combobox.addItem(frequency)

    def update_dac_config(self):
        if self.updating:
            return

        self.updating = True

        self.update_frequency_options()
        self.show_signal_frequency()
        self.get_frequency_info()

        self.updating = False

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create the main window
    main_window = QMainWindow()
    main_window.setWindowTitle("DAC Bram Settings")

    # Create an instance of DacBramSettingsTab
    dac_bram_settings_tab = DacBramSettingsTab()

    # Set the DacBramSettingsTab as the central widget of the main window
    main_window.setCentralWidget(dac_bram_settings_tab)

    # Show the main window
    main_window.show()

    sys.exit(app.exec())
