from PyQt6.QtWidgets import (
    QPushButton,
    QButtonGroup,
    QCheckBox,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QGroupBox,
    QLineEdit,
    QLabel,
    QRadioButton,
)
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from PyQt6.QtCore import pyqtSlot, pyqtSignal

from source import initDacBram, stop_sweep
from AdcReceiver import pita, AdcReceiverThread
from SignalManager import DacSignalManager

MHZ_MAX_DAC_FREQ = 125

class StartStopButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setText("Start")
        self.setCheckable(True)
        self.setStyleSheet("QPushButton {background-color: green;}")
        self.setFixedSize(50, 30)

    def toggle_button(self):
        if self.isChecked():
            self.setText("Stop")
            self.setStyleSheet(f"QPushButton {{background-color: red;}}")
        else:
            self.setText("Start")
            self.setStyleSheet(f"QPushButton {{background-color: green;}}")



class DacBramSettingsTab(QGroupBox):
    update_adc = pyqtSignal()

    def __init__(self, adcreceiver: AdcReceiverThread, channel):
        super().__init__()

        # adcReceiverObject:
        self.adcreceiver = adcreceiver

        # bram-dac channel
        self.channel = channel

        # default object variables for config:
        self.dwell_time_ms = "8e-06"
        self.dac_steps = 1000
        self.signal_type = "Sine"
        self.start_V = 0
        self.stop_V = 1
        self.amplitude = 1
        self.reset_voltage = 0

        self.setupUI()

        # Initialise SignalManager to connect signals and slots
        self.DacSignalManager = DacSignalManager()
        self.DacSignalManager.connect_signals(self)

        # Display settings as soon as the GUI starts
        self.update_frequency_options()
        self.update_signal_options()
        self.get_frequency_info()

    def setupUI(self):
        self.port_layout = QHBoxLayout()
        self.setLayout(self.port_layout)

        # First column of the Dac Bram Setting Groupbox
        self.first_column = QVBoxLayout()
        self.start_sweep_button = StartStopButton()
        self.reset_voltage_label = QLabel("Reset Voltage")
        self.reset_voltage_edit = QLineEdit()
        self.reset_voltage_edit.setText(str(self.reset_voltage))
        self.reset_voltage_edit.setValidator(
            QDoubleValidator()
        )  # only floating points are accepted for reset voltage
        self.first_column.addWidget(self.start_sweep_button)
        self.first_column.addWidget(self.reset_voltage_label)
        self.first_column.addWidget(self.reset_voltage_edit)

        # Signal type checkboxes with additional inputs
        self.signal_box = QGroupBox("Signal Type and Parameters")
        self.signal_layout = QVBoxLayout()
        self.signal_button_group = QButtonGroup(self)
        self.signal_box.setLayout(self.signal_layout)

        # Create horizontal layout for each signal type and its parameters
        self.sine_layout = QHBoxLayout()
        self.sine_button = QCheckBox("Sine")
        self.sine_button.setChecked(True)
        self.amplitude_label = QLabel("Amplitude:")
        self.amplitude_edit = QLineEdit()

        self.amplitude_edit.setText(str(self.amplitude))

        self.sine_layout.addWidget(self.sine_button)
        self.sine_layout.addWidget(self.amplitude_label)
        self.sine_layout.addWidget(self.amplitude_edit)
        self.signal_layout.addLayout(self.sine_layout)

        self.squareroot_button = QCheckBox("Square Root")
        self.start_voltage_label = QLabel("Start Voltage:")
        self.start_voltage_edit = QLineEdit()
        self.start_voltage_edit.setText(str(self.start_V))
        self.stop_voltage_label = QLabel("Stop Voltage:")
        self.stop_voltage_edit = QLineEdit()
        self.stop_voltage_edit.setText(str(self.stop_V))

        self.signal_layout.addWidget(self.squareroot_button)

        # Only floating points accepted as amplitude, start- and stopVoltage
        self.amplitude_edit.setValidator(QDoubleValidator())
        self.start_voltage_edit.setValidator(QDoubleValidator())
        self.stop_voltage_edit.setValidator(QDoubleValidator())

        self.sawtooth_layout = QHBoxLayout()
        self.sawtooth_button = QCheckBox("Sawtooth")
        self.sawtooth_layout.addWidget(self.sawtooth_button)
        self.sawtooth_layout.addWidget(self.start_voltage_label)
        self.sawtooth_layout.addWidget(self.start_voltage_edit)
        self.sawtooth_layout.addWidget(self.stop_voltage_label)
        self.sawtooth_layout.addWidget(self.stop_voltage_edit)
        self.signal_layout.addLayout(self.sawtooth_layout)

        self.signal_button_group.addButton(self.sine_button)
        self.signal_button_group.addButton(self.squareroot_button)
        self.signal_button_group.addButton(self.sawtooth_button)


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
        self.port_layout.addLayout(self.first_column)
        self.port_layout.addWidget(self.signal_box)
        self.port_layout.addWidget(self.frequency_box)

    def get_reset_voltage(self):
        """get current reset voltage"""

        self.reset_voltage = float(self.reset_voltage_edit.text())

    def get_signal_info(self):
        """
        Get selected signal type and its parameters.
        """

        if self.sine_button.isChecked():
            self.signal_type = "Sine"
            self.amplitude = float(self.amplitude_edit.text())
        else:
            if self.squareroot_button.isChecked():
                self.signal_type = "Square Root"
            else:
                self.signal_type = "Sawtooth"

            self.start_V = float(self.start_voltage_edit.text())
            self.stop_V = float(self.stop_voltage_edit.text())

    def update_frequency_options(self):
        if self.dac_sample_rate_button.isChecked():
            self.dac_sample_rate_combobox.setVisible(True)
            self.signal_frequency_combobox.setVisible(False)
        else:
            self.dac_sample_rate_combobox.setVisible(False)
            self.signal_frequency_combobox.setVisible(True)
    
    def update_signal_options(self):
        if self.sine_button.isChecked():
            self.amplitude_label.setVisible(True)
            self.amplitude_edit.setVisible(True)
            self.start_voltage_label.setVisible(False)
            self.start_voltage_edit.setVisible(False)
            self.stop_voltage_label.setVisible(False)
            self.stop_voltage_edit.setVisible(False)
        else:
            self.amplitude_label.setVisible(False)
            self.amplitude_edit.setVisible(False)
            self.start_voltage_label.setVisible(True)
            self.start_voltage_edit.setVisible(True)
            self.stop_voltage_label.setVisible(True)
            self.stop_voltage_edit.setVisible(True)

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

    @pyqtSlot()
    def sweep_button_clicked(self):
        self.start_sweep_button.toggle_button()
        if self.start_sweep_button.isChecked():
            if self.adcreceiver.isRunning:
                self.adcreceiver.stop()

            self.get_signal_info()
            self.get_frequency_info()
            initDacBram(
                pita,
                self.signal_type,
                self.amplitude,
                self.start_V,
                self.stop_V,
                self.dac_steps,
                self.dwell_time_ms,
                self.channel,
            )
        else:
            self.get_reset_voltage()
            stop_sweep(pita, self.channel, self.reset_voltage)
        self.update_adc.emit()

    @pyqtSlot()
    def update_dac_config(self):
        self.update_signal_options()
        self.update_frequency_options()
        self.get_frequency_info()
        
        if self.start_sweep_button.isChecked():
            if self.adcreceiver.isRunning():
                self.adcreceiver.stop()

            self.get_signal_info()
            initDacBram(
                pita,
                self.signal_type,
                self.amplitude,
                self.start_V,
                self.stop_V,
                self.dac_steps,
                self.dwell_time_ms,
                self.channel,
            )
        self.update_adc.emit()
