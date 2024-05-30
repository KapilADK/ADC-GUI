import sys
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, 
                             QCheckBox, QHBoxLayout, QButtonGroup, QComboBox, QGroupBox, 
                             QLineEdit, QLabel)
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QDoubleValidator

# Make sure to import these correctly
from rp.adc.helpers import unpackADCData
from source import *
from AdcReceiver import *
from rp.constants import ALL_BRAM_DAC_PORTS

verbose = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Data Acquisition in Block Mode")
        self.setFixedSize(800, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Group box for all ADC settings
        self.settings_group = QGroupBox("ADC Receiver Settings")
        self.settings_layout = QHBoxLayout()
        self.settings_group.setLayout(self.settings_layout)

        # Create start button
        self.start_plot_button = QPushButton("START Plot")
        self.start_plot_button.setCheckable(True)
        self.start_plot_button.setStyleSheet("QPushButton {background-color: green;}")
        self.start_plot_button.setFixedSize(90, 30)

        # ComboBox for ADC sample rate selection
        self.adc_sr_group = QGroupBox("ADC Sample Rate")
        self.adc_sr_layout = QVBoxLayout(self.adc_sr_group)
        self.adc_sr_menu = QComboBox()
        possible_sr = [125, 62.5, 31.25, 25, 15.625, 12.5, 7.8125, 6.25, 5, 3.90625, 3.125, 2.5, 1.25, 1, 0.625, 0.5]
        for sr in possible_sr:
            self.adc_sr_menu.addItem(f"{sr} MHz")
        self.adc_sr_layout.addWidget(self.adc_sr_menu)

        # Radio buttons for channel selection
        self.channel_group = QGroupBox("Channel Selection")
        self.channel_layout = QVBoxLayout()
        self.channel_button_group = QButtonGroup(self)
        self.channel1_button = QCheckBox("Channel 1")
        self.channel2_button = QCheckBox("Channel 2")
        self.both_button = QCheckBox("Both")
        self.channel1_button.setChecked(True)
        self.channel_button_group.addButton(self.channel1_button)
        self.channel_button_group.addButton(self.channel2_button)
        self.channel_button_group.addButton(self.both_button)
        self.channel_layout.addWidget(self.channel1_button)
        self.channel_layout.addWidget(self.channel2_button)
        self.channel_layout.addWidget(self.both_button)
        self.channel_group.setLayout(self.channel_layout)

        # Add adc mode (sync oder async)
        self.mode_group = QGroupBox("ADC Mode")
        self.mode_layout = QVBoxLayout()
        self.mode_button_group = QButtonGroup(self)
        self.async_mode_button = QCheckBox("Async")
        self.sync_mode_button = QCheckBox("Sync")
        self.sync_mode_button.setChecked(True)
        self.mode_button_group.addButton(self.async_mode_button)
        self.mode_button_group.addButton(self.sync_mode_button)
        self.mode_layout.addWidget(self.async_mode_button)
        self.mode_layout.addWidget(self.sync_mode_button)
        self.mode_group.setLayout(self.mode_layout)

        # Add required time to write the RAM 
        self.time_group = QGroupBox("Time to write RAM in ms")
        self.time_layout = QVBoxLayout(self.time_group)
        self.time_menu = QComboBox()
        possible_time = [10, 20, 50, 100, 200]
        for time in possible_time:
            self.time_menu.addItem(f"{time} ms")
        self.output_ram_size_layout = QHBoxLayout()
        self.output_text = QLabel("RAM Size:")
        self.output_ram_size = QLabel()
        self.output_ram_size_layout.addWidget(self.output_text)
        self.output_ram_size_layout.addWidget(self.output_ram_size)
        self.time_layout.addWidget(self.time_menu)
        self.time_layout.addLayout(self.output_ram_size_layout)

        # Add settings to the horizontal layout
        self.settings_layout.addWidget(self.start_plot_button)
        self.settings_layout.addWidget(self.adc_sr_group)
        self.settings_layout.addWidget(self.channel_group)
        self.settings_layout.addWidget(self.mode_group)
        self.settings_layout.addWidget(self.time_group)

        # Add the settings group box to the main layout
        self.main_layout.addWidget(self.settings_group)

        # Create DAC-BRAM settings group box
        self.dac_bram_group = QGroupBox("DAC-BRAM Settings")
        self.dac_bram_layout = QHBoxLayout()
        self.dac_bram_group.setLayout(self.dac_bram_layout)

        # Create start button
        self.start_sweep_button = QPushButton("START Sweep")
        self.start_sweep_button.setCheckable(True)
        self.start_sweep_button.setStyleSheet("QPushButton {background-color: green;}")
        self.start_sweep_button.setFixedSize(95, 30)

        # Signal type checkboxes with additional inputs
        self.signal_group = QGroupBox("Signal Type and Parameters")
        self.signal_layout = QVBoxLayout()
        self.signal_button_group = QButtonGroup(self)
        self.signal_group.setLayout(self.signal_layout)

        # Create horizontal layout for each signal type and its parameters
        self.sine_layout = QHBoxLayout()
        self.sine_button = QCheckBox("Sine")
        self.sine_button.setChecked(True)
        self.amplitude_label = QLabel("Amplitude:")
        self.amplitude_input = QLineEdit()
        self.sine_layout.addWidget(self.sine_button)
        self.sine_layout.addWidget(self.amplitude_label)
        self.sine_layout.addWidget(self.amplitude_input)
        self.signal_layout.addLayout(self.sine_layout)

        self.squareroot_layout = QHBoxLayout()
        self.squareroot_button = QCheckBox("Square Root")
        self.start_voltage_label = QLabel("Start Voltage:")
        self.start_voltage_input = QLineEdit()
        self.stop_voltage_label = QLabel("Stop Voltage:")
        self.stop_voltage_input = QLineEdit()
        self.squareroot_layout.addWidget(self.squareroot_button)
        self.squareroot_layout.addWidget(self.start_voltage_label)
        self.squareroot_layout.addWidget(self.start_voltage_input)
        self.squareroot_layout.addWidget(self.stop_voltage_label)
        self.squareroot_layout.addWidget(self.stop_voltage_input)
        self.signal_layout.addLayout(self.squareroot_layout)

        self.amplitude_input.setValidator(QDoubleValidator())
        self.start_voltage_input.setValidator(QDoubleValidator())
        self.stop_voltage_input.setValidator(QDoubleValidator())

        # Connect signal to slot for checking input validity
        self.amplitude_input.textChanged.connect(self.validate_amplitude)
        self.start_voltage_input.textChanged.connect(self.validate_start_voltage)
        self.stop_voltage_input.textChanged.connect(self.validate_stop_voltage)

        self.sawtooth_layout = QHBoxLayout()
        self.sawtooth_button = QCheckBox("Sawtooth")
        self.sawtooth_layout.addWidget(self.sawtooth_button)
        self.sawtooth_layout.addWidget(self.start_voltage_label)
        self.sawtooth_layout.addWidget(self.start_voltage_input)
        self.sawtooth_layout.addWidget(self.stop_voltage_label)
        self.sawtooth_layout.addWidget(self.stop_voltage_input)
        self.signal_layout.addLayout(self.sawtooth_layout)

        self.signal_button_group.addButton(self.sine_button)
        self.signal_button_group.addButton(self.squareroot_button)
        self.signal_button_group.addButton(self.sawtooth_button)

        # Add the signal group box to the DAC-BRAM layout
        self.dac_bram_layout.addWidget(self.start_sweep_button)
        self.dac_bram_layout.addWidget(self.signal_group)

        # Add the DAC-BRAM group box to the main layout
        self.main_layout.addWidget(self.dac_bram_group)

        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(True, True)
        self.plot_widget.setLabel('left', 'Voltage', units='V')
        self.plot_widget.setLabel('bottom', 'time', units='s')
        self.plot_widget.addLegend()

        self.x_data = np.zeros(1000)
        self.y_data_ch1 = np.zeros(1000)
        self.plot_graph_ch1 = self.plot_widget.plot(self.x_data, self.y_data_ch1, pen='r', name='Channel 1')
        self.y_data_ch2 = np.zeros(1000)
        self.plot_graph_ch2 = self.plot_widget.plot(self.x_data, self.y_data_ch2, pen='b', name='Channel 2')

        # Add the plot widget to the main layout
        self.main_layout.addWidget(self.plot_widget)

        # Connect signal to slot
        self.start_plot_button.clicked.connect(self.button_clicked)
        self.start_sweep_button.clicked.connect(self.sweep_button_clicked)
        self.sine_button.toggled.connect(self.update_signal_options)
        self.squareroot_button.toggled.connect(self.update_signal_options)
        self.sawtooth_button.toggled.connect(self.update_signal_options)

        self.update_signal_options()
        self.display_ram_size()

    @pyqtSlot()
    def button_clicked(self):
        if self.start_plot_button.isChecked():
            self.start_plot_button.setText("STOP Plot")
            self.start_plot_button.setStyleSheet("QPushButton {background-color: red;}")
            self.set_settings_enabled(False)
            self.sample_rate, self.mode = self.get_adc_config()
            self.plot_graph_ch1.clear()
            self.plot_graph_ch2.clear()
            self.adcreceiver = AdcReceiverThread(self.sample_rate, self.mode)
            self.adcreceiver.dataReceived.connect(self.update_plot)
            self.adcreceiver.start()
        else:
            self.start_plot_button.setText("START Plot")
            self.start_plot_button.setStyleSheet("QPushButton {background-color: green;}")
            self.set_settings_enabled(True)
            self.adcreceiver.terminate()

    @pyqtSlot()
    def sweep_button_clicked(self):
        if self.start_sweep_button.isChecked():
            self.start_sweep_button.setText("STOP Sweep")
            self.start_sweep_button.setStyleSheet("QPushButton {background-color: red;}")
            signal, start_V, stop_V = self.get_dac_config()
            self.dacbramconfigurator = DacBramConfigurator(signal, start_V, stop_V)
            self.dacbramconfigurator.start()
            pita.start_dac_sweep(ALL_BRAM_DAC_PORTS)
        else:
            self.start_sweep_button.setText("START Sweep")
            self.start_sweep_button.setStyleSheet("QPushButton {background-color: green;}")
            self.dacbramconfigurator.terminate()
            pita.stop_dac_sweep()

    def get_adc_config(self):
        sample_rate = float(self.adc_sr_menu.currentText().split()[0])
        if self.sync_mode_button.isChecked():
            mode = "Sync"
        else:
            mode = "Async"
        
        return sample_rate, mode

    def get_dac_config(self):
        if self.sine_button.isChecked():
            signal_type = "Sine"
            amplitude = float(self.amplitude_input.text())
            return signal_type, amplitude, 0
        elif self.squareroot_button.isChecked():
            signal_type = "Square Root"
            start_V = float(self.start_voltage_input.text())
            stop_V = float(self.stop_voltage_input.text())
            return signal_type, start_V, stop_V
        elif self.sawtooth_button.isChecked():
            signal_type = "Sawtooth"
            start_V = float(self.start_voltage_input.text())
            stop_V = float(self.stop_voltage_input.text())
            return signal_type, start_V, stop_V

    def set_settings_enabled(self, enabled):
        self.adc_sr_menu.setEnabled(enabled)
        self.channel1_button.setEnabled(enabled)
        self.channel2_button.setEnabled(enabled)
        self.both_button.setEnabled(enabled)
        self.sync_mode_button.setEnabled(enabled)
        self.async_mode_button.setEnabled(enabled)
        self.time_menu.setEnabled(enabled)

    def display_ram_size(self):
        pass

    @pyqtSlot(str)
    def validate_amplitude(self, text):
        if text:
            try:
                float(text)
            except ValueError:
                return False
        return True

    @pyqtSlot(str)
    def validate_start_voltage(self, text):
        if text:
            try:
                float(text)
            except ValueError:
                return False
        return True

    @pyqtSlot(str)
    def validate_stop_voltage(self, text):
        if text:
            try:
                float(text)
            except ValueError:
                return False
        return True

    @pyqtSlot()
    def update_signal_options(self):
        if self.sine_button.isChecked():
            self.amplitude_label.setVisible(True)
            self.amplitude_input.setVisible(True)
            self.start_voltage_label.setVisible(False)
            self.start_voltage_input.setVisible(False)
            self.stop_voltage_label.setVisible(False)
            self.stop_voltage_input.setVisible(False)
        else:
            self.amplitude_label.setVisible(False)
            self.amplitude_input.setVisible(False)
            self.start_voltage_label.setVisible(True)
            self.start_voltage_input.setVisible(True)
            self.stop_voltage_label.setVisible(True)
            self.stop_voltage_input.setVisible(True)

    @pyqtSlot(bytes)
    def update_plot(self, data_raw):
        data = unpackADCData(
            np.frombuffer(data_raw, dtype=np.int32),
            1,
            rawData=False,
        )
        self.y_data_ch1 = data[0]
        self.y_data_ch2 = data[1]
        
        total_samples = len(self.y_data_ch1)  # both channels have the same number of samples
        total_time = total_samples / (self.sample_rate * 1e6)  # Convert sample rate from MHz to Hz
        self.x_data = np.linspace(0, total_time, total_samples)

        if self.channel1_button.isChecked():
            self.plot_graph_ch1.setData(self.x_data, self.y_data_ch1)
        elif self.channel2_button.isChecked():
            self.plot_graph_ch2.setData(self.x_data, self.y_data_ch2)
        else:
            self.plot_graph_ch1.setData(self.x_data, self.y_data_ch1)
            self.plot_graph_ch2.setData(self.x_data, self.y_data_ch2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
