from PyQt6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QCheckBox,
    QHBoxLayout,
    QButtonGroup,
    QComboBox,
    QGroupBox,
    QLineEdit,
    QLabel,
    QRadioButton,
    QApplication,
)
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import pyqtSlot, pyqtSignal
import sys
import time

from source import initDacBram, stop_sweep
from AdcReceiver import pita

MHZ_MAX_DAC_FREQ = 25


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


class DacBramSettingsTab(QGroupBox):  # QGroupBox
    restart_adc = pyqtSignal()

    def __init__(self, adcreceiver, channel):
        super().__init__()

        # adcReceiverObject:
        self.adcreceiver = adcreceiver

        # bram-dac channel
        self.channel = channel

        # default object variables for config:
        self.dwell_time_ms = "4e-05"
        self.dac_steps = 10
        self.signal_type = "Sine"
        self.start_V = 0
        self.stop_V = 1
        self.amplitude = 1
        self.reset_voltage = 0

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

        self.squareroot_layout = QHBoxLayout()
        self.squareroot_button = QCheckBox("Square Root")
        self.start_voltage_label = QLabel("Start Voltage:")
        self.start_voltage_edit = QLineEdit()
        self.start_voltage_edit.setText(str(self.start_V))
        self.stop_voltage_label = QLabel("Stop Voltage:")
        self.stop_voltage_edit = QLineEdit()
        self.stop_voltage_edit.setText(str(self.stop_V))

        self.squareroot_layout.addWidget(self.squareroot_button)
        self.squareroot_layout.addWidget(self.start_voltage_label)
        self.squareroot_layout.addWidget(self.start_voltage_edit)
        self.squareroot_layout.addWidget(self.stop_voltage_label)
        self.squareroot_layout.addWidget(self.stop_voltage_edit)
        self.signal_layout.addLayout(self.squareroot_layout)

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
        dac_sample_rates = [
            25,
            15.625,
            12.5,
            7.8125,
            6.25,
            5,
            3.90625,
            3.125,
            2.5,
            1.25,
            1,
            0.625,
            0.5,
        ]
        for dac_sample_rate in dac_sample_rates:
            self.dac_sample_rate_combobox.addItem(f"{dac_sample_rate} MHz")
        self.dac_steps_label = QLabel("DAC Steps")
        self.dac_steps_edit = QLineEdit()
        self.dac_steps_edit.setText(str(self.dac_steps))
        self.dwell_time_ms_label = QLabel("Dwell time(ms):")
        self.show_dwell_time_ms_label = QLabel()
        self.show_dwell_time_ms_label.setText(str(self.dwell_time_ms))

        self.dac_sample_rate_layout.addWidget(self.dac_sample_rate_button)
        self.dac_sample_rate_layout.addWidget(self.dac_sample_rate_combobox)
        self.dac_sample_rate_layout.addWidget(self.dac_steps_label)
        self.dac_sample_rate_layout.addWidget(self.dac_steps_edit)
        self.dac_sample_rate_layout.addWidget(self.dwell_time_ms_label)
        self.dac_sample_rate_layout.addWidget(self.show_dwell_time_ms_label)

        self.signal_frequency_layout = QHBoxLayout()
        self.signal_frequency_button = QRadioButton("Signal Frequency")
        self.signal_frequency_combobox = QComboBox()
        frequencies = [
            2.5,
            1.25,
            625,
            500,
            312.5,
            250,
            156.3,
            125,
            100,
            78.1,
            62.5,
            50,
            25,
            20,
            12.5,
            10,
        ]
        for MHz_frequency in frequencies[:2]:
            self.signal_frequency_combobox.addItem(f"{MHz_frequency} MHz")
        for KHz_frequencies in frequencies[2:]:
            self.signal_frequency_combobox.addItem(f"{KHz_frequencies} KHz")
        self.max_dac_steps_label = QLabel("Max. DAC steps:")
        self.show_max_dac_steps_label = QLabel()

        self.signal_frequency_layout.addWidget(self.signal_frequency_button)
        self.signal_frequency_layout.addWidget(self.signal_frequency_combobox)
        self.signal_frequency_layout.addWidget(self.max_dac_steps_label)
        self.signal_frequency_layout.addWidget(self.show_max_dac_steps_label)

        self.frequency_box_layout.addLayout(self.dac_sample_rate_layout)
        self.frequency_box_layout.addLayout(self.signal_frequency_layout)

        # Add each box/layout to the Port layout
        self.port_layout.addLayout(self.first_column)
        self.port_layout.addWidget(self.signal_box)
        self.port_layout.addWidget(self.frequency_box)

        # Connect signals to slots
        #####################################################################
        self.start_sweep_button.clicked.connect(self.sweep_button_clicked)
        self.sine_button.toggled.connect(self.update_signal_options)
        self.squareroot_button.toggled.connect(self.update_signal_options)

        self.dac_sample_rate_button.toggled.connect(self.update_frequency_options)
        self.dac_sample_rate_button.toggled.connect(self.get_frequency_info)
        self.dac_sample_rate_button.toggled.connect(self.set_max_dac_steps)
        self.dac_sample_rate_combobox.currentIndexChanged.connect(
            self.get_frequency_info
        )
        self.signal_frequency_combobox.currentIndexChanged.connect(
            self.get_frequency_info
        )
        self.signal_frequency_combobox.currentIndexChanged.connect(
            self.set_max_dac_steps
        )
        self.dac_steps_edit.textChanged.connect(self.get_frequency_info)
        self.dac_steps_edit.textChanged.connect(self.validate_dac_steps)
        self.dac_sample_rate_button.toggled.connect(
            self.validate_dac_steps_upon_button_toggled
        )
        self.signal_frequency_combobox.currentIndexChanged.connect(
            self.validate_dac_steps_upon_button_toggled
        )

        self.sine_button.toggled.connect(self.update_dac_config)
        self.squareroot_button.toggled.connect(self.update_dac_config)
        self.sawtooth_button.toggled.connect(self.update_dac_config)
        self.amplitude_edit.returnPressed.connect(self.update_dac_config)
        self.start_voltage_edit.returnPressed.connect(self.update_dac_config)
        self.stop_voltage_edit.returnPressed.connect(self.update_dac_config)
        self.dac_sample_rate_combobox.currentIndexChanged.connect(
            self.update_dac_config
        )
        self.dac_steps_edit.returnPressed.connect(self.update_dac_config)
        self.signal_frequency_combobox.currentIndexChanged.connect(
            self.update_dac_config
        )
        self.dac_sample_rate_button.toggled.connect(self.update_dac_config)
        ###########################################################################

        # Display settings as soon as the GUI starts
        self.update_signal_options()
        self.update_frequency_options()
        self.get_frequency_info()
        self.set_max_dac_steps()

    def get_reset_voltage(self):
        """get current reset voltage"""
        self.reset_voltage = float(self.reset_voltage_edit.text())

    @pyqtSlot()
    def sweep_button_clicked(self):
        self.start_sweep_button.toggle_button()
        if self.start_sweep_button.isChecked():
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

    @pyqtSlot()
    def update_dac_config(self):
        time.sleep(0.1)
        if self.start_sweep_button.isChecked():
            if self.adcreceiver.isRunning():
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
        self.restart_adc.emit()

    def get_signal_info(self):
        """
        Get selected signal type and its parameters.

        returns
        -------
        signal_type : string
        start_V: float
        stop_V : float
        """

        if self.sine_button.isChecked():
            self.signal_type = "Sine"
            self.amplitude = float(self.amplitude_edit.text())
        else:
            if self.squareroot_button.isChecked():
                self.signal_type = "Square Root"
                self.start_V = float(self.start_voltage_edit.text())
                self.stop_V = float(self.stop_voltage_edit.text())
            else:
                if self.sawtooth_button.isChecked():
                    self.signal_type = "Sawtooth"
                    self.start_V = float(self.start_voltage_edit.text())
                    self.stop_V = float(self.stop_voltage_edit.text())

    def get_frequency_info(self):
        """
        Get dwell time and DAC steps to configure sample rate of DAC.

        returns
        -------
        dac_steps : int
        dwel_time_ms : float
        """
        try:
            self.dac_steps = int(self.dac_steps_edit.text())
        except ValueError:
            return False
        if self.dac_sample_rate_button.isChecked():
            self.dac_sample_rate = float(
                self.dac_sample_rate_combobox.currentText().split()[0]
            )
            self.dwell_time_ms = 1 / (self.dac_sample_rate * 1e3)
        elif self.signal_frequency_button.isChecked():
            self.signal_frequency = float(
                self.signal_frequency_combobox.currentText().split()[0]
            )
            if self.signal_frequency == 2.5 or self.signal_frequency == 1.25:
                self.dwell_time_ms = 1 / (self.signal_frequency * 1e3 * self.dac_steps)
            else:
                self.dwell_time_ms = 1 / (self.signal_frequency * self.dac_steps)

        self.show_dwell_time_ms_label.setText(str(self.dwell_time_ms))

    @pyqtSlot(str)
    def validate_dac_steps(self, text):
        self.set_max_dac_steps()
        if text and int(text) > self.max_dac_steps:
            # Revert the input to the previous valid state
            cursor_position = self.dac_steps_edit.cursorPosition()
            self.dac_steps_edit.setText(text[:-1])
            self.dac_steps_edit.setCursorPosition(cursor_position - 1)

    def set_max_dac_steps(self):
        """
        Shows the max. dac steps that can be given when certain signal frequency is desired
        """

        if self.dac_sample_rate_button.isChecked():
            self.max_dac_steps = 2500
        else:
            signal_frequency = float(
                self.signal_frequency_combobox.currentText().split()[0]
            )
            if signal_frequency == 2.5 or signal_frequency == 1.25:
                self.max_dac_steps = int(MHZ_MAX_DAC_FREQ / signal_frequency)
            else:
                self.max_dac_steps = int(MHZ_MAX_DAC_FREQ / (signal_frequency / 1000))

        self.show_max_dac_steps_label.setText(str(self.max_dac_steps))

    @pyqtSlot()
    def validate_dac_steps_upon_button_toggled(self):
        if int(self.dac_steps_edit.text()) > int(self.show_max_dac_steps_label.text()):
            self.dac_steps_edit.setText(str(self.show_max_dac_steps_label.text()))

    @pyqtSlot()
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

    @pyqtSlot()
    def update_frequency_options(self):
        if self.dac_sample_rate_button.isChecked():
            self.dac_sample_rate_combobox.setVisible(True)
            self.signal_frequency_combobox.setVisible(False)
        else:
            self.dac_sample_rate_combobox.setVisible(False)
            self.signal_frequency_combobox.setVisible(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DacBramSettingsTab(1, None)
    window.show()
    sys.exit(app.exec())
