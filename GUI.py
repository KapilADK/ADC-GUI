import sys
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (QApplication, 
                             QMainWindow, 
                             QPushButton, 
                             QVBoxLayout, 
                             QWidget,
                             QCheckBox,
                             QHBoxLayout,
                             QButtonGroup,
                             QComboBox,
                             QGroupBox,
                             QLineEdit,
                             QLabel,
)   
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QDoubleValidator

from rp.adc.helpers import unpackADCData
from source import *
from AdcReceiver import AdcReceiverThread 

verbose = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Data Acquisition in Block Mode")
        self.setFixedSize(800, 800)

        # Create widget object
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Group box for all ADC settings
        self.settings_group = QGroupBox("ADC Settings")
        self.settings_layout = QVBoxLayout()
        self.settings_group.setLayout(self.settings_layout)

        # Create horizontal layout for ADC Sample Rate, Channel Selection, and RAM Size
        self.settings_row_layout = QHBoxLayout()

        # Create start button
        self.start_button = QPushButton("START")
        self.start_button.setCheckable(True)
        self.start_button.setStyleSheet("QPushButton {background-color: green;}")
        self.start_button.setFixedSize(60, 30)

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

        # Add settings to the horizontal layout
        self.settings_row_layout.addWidget(self.start_button)
        self.settings_row_layout.addWidget(self.adc_sr_group)
        self.settings_row_layout.addWidget(self.channel_group)

        # Add the horizontal layout to the settings layout
        self.settings_layout.addLayout(self.settings_row_layout)

        # Add the settings group box to the main layout
        self.main_layout.addWidget(self.settings_group)

        # Create DAC-BRAM settings group box
        self.dac_bram_group = QGroupBox("DAC-BRAM Settings")
        self.dac_bram_layout = QVBoxLayout()
        self.dac_bram_group.setLayout(self.dac_bram_layout)

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
        self.squareroot_button = QCheckBox("Square root")
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
        self.dac_bram_layout.addWidget(self.signal_group)

        # Add the DAC-BRAM group box to the main layout
        self.main_layout.addWidget(self.dac_bram_group)

        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(True, True)
        self.plot_widget.setLabel('left', 'Voltage', units='V')
        self.plot_widget.setLabel('bottom', 'time', )
        self.plot_widget.addLegend()

        self.y_data_ch1 = np.ones(len(range(1000)))
        self.plot_graph_ch1 = self.plot_widget.plot(self.y_data_ch1, pen='r', name='Channel 1')
        self.y_data_ch2 = np.ones(len(range(1000)))
        self.plot_graph_ch2 = self.plot_widget.plot(self.y_data_ch2, pen='b', name='Channel2')

        # Add the plot widget to the main layout
        self.main_layout.addWidget(self.plot_widget)

        # Connect signal to slot
        self.start_button.clicked.connect(self.button_clicked)
        self.sine_button.toggled.connect(self.update_signal_options)
        self.squareroot_button.toggled.connect(self.update_signal_options)
        self.sawtooth_button.toggled.connect(self.update_signal_options)

        self.update_signal_options()



    @pyqtSlot()
    def button_clicked(self):
        if self.start_button.isChecked():
            self.start_button.setText("STOP")
            self.start_button.setStyleSheet("QPushButton {background-color: red;}")
            self.set_settings_enabled(False)
            sample_rate, signal, start_V, stop_V = self.get_values()
            self.plot_graph_ch1.clear()
            self.plot_graph_ch2.clear()
            self.adcreceiverthread = AdcReceiverThread(sample_rate, signal, start_V, stop_V)
            self.adcreceiverthread.dataReceived.connect(self.update_plot)
            self.adcreceiverthread.start()
            
        else:
            self.start_button.setText("START")
            self.start_button.setStyleSheet("QPushButton {background-color: green;}")
            self.set_settings_enabled(True)
            self.adcreceiverthread.terminate()

    def get_values(self):
        self.selected_adc_sr = float(self.adc_sr_menu.currentText().split()[0])
        if self.sine_button.isChecked():
            self.signal_type = "Sine"
            self.amplitude = float(self.amplitude_input.text())

        elif self.squareroot_button.isChecked():
            self.signal_type = "Square Root"
            self.start_V = float(self.start_voltage_input.text())
            self.stop_V = float(self.stop_voltage_input.text())

        elif self.sawtooth_button.isChecked():
            self.signal_type = "Sawtooth"
            self.start_V = float(self.start_voltage_input.text())
            self.stop_V = float(self.stop_voltage_input.text())

        if self.signal_type == "Sine":
            return self.selected_adc_sr, self.signal_type, self.amplitude, 0
        return self.selected_adc_sr, self.signal_type, self.start_V, self.stop_V

    def set_settings_enabled(self, enabled):
        self.adc_sr_menu.setEnabled(enabled)
        self.channel1_button.setEnabled(enabled)
        self.channel2_button.setEnabled(enabled)
        self.both_button.setEnabled(enabled)
        self.sine_button.setEnabled(enabled)
        self.squareroot_button.setEnabled(enabled)
        self.sawtooth_button.setEnabled(enabled)
        self.amplitude_input.setEnabled(enabled)
        self.start_voltage_input.setEnabled(enabled)
        self.stop_voltage_input.setEnabled(enabled)

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

        if self.channel1_button.isChecked():
            self.plot_graph_ch1.setData(self.y_data_ch1)
        elif self.channel2_button.isChecked():
            self.plot_graph_ch2.setData(self.y_data_ch2)
        else:
            self.plot_graph_ch1.setData(self.y_data_ch1)
            self.plot_graph_ch2.setData(self.y_data_ch2)
            


def start():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    start()
