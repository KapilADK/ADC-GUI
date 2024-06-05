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
                             QRadioButton,
                            )
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import  QDoubleValidator, QIntValidator

from rp.adc.helpers import unpackADCData
from AdcReceiver import AdcReceiverThread, DacBramConfigurator, MHZ_MAX_DAC_FREQ, pita
from rp.constants import ALL_BRAM_DAC_PORTS

verbose = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Data Acquisition in Block Mode")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Group box for all ADC settings
        self.adc_settings_box = QGroupBox("ADC Receiver Settings")
        self.adc_settings_layout = QHBoxLayout()
        self.adc_settings_box.setLayout(self.adc_settings_layout)

        # Create start button
        self.start_plot_button = QPushButton("START Plot")
        self.start_plot_button.setCheckable(True)
        self.start_plot_button.setStyleSheet("QPushButton {background-color: green;}")
        self.start_plot_button.setFixedSize(90, 30)

        # ComboBox for ADC sample rate selection
        self.adc_sample_rate_box = QGroupBox("ADC Sample Rate")
        self.adc_sample_rate_layout = QVBoxLayout(self.adc_sample_rate_box)
        self.adc_sample_rate_combobox = QComboBox()
        adc_sample_rates = [125, 62.5, 31.25, 25, 15.625, 12.5, 7.8125, 6.25, 5, 3.90625, 3.125, 2.5, 1.25, 1, 0.625, 0.5]
        for adc_sample_rate in adc_sample_rates:
            self.adc_sample_rate_combobox.addItem(f"{adc_sample_rate} MHz")
        self.adc_sample_rate_layout.addWidget(self.adc_sample_rate_combobox)

        # Checkbox for channel selection
        self.channel_box = QGroupBox("Channel Selection")
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
        self.channel_box.setLayout(self.channel_layout)

        # Add adc mode (sync oder async)
        self.mode_box = QGroupBox("ADC Mode")
        self.mode_layout = QVBoxLayout()
        self.mode_button_group = QButtonGroup(self)
        self.async_mode_button = QCheckBox("Async")
        self.sync_mode_button = QCheckBox("Sync")
        self.sync_mode_button.setChecked(True)
        self.mode_button_group.addButton(self.async_mode_button)
        self.mode_button_group.addButton(self.sync_mode_button)
        self.mode_layout.addWidget(self.async_mode_button)
        self.mode_layout.addWidget(self.sync_mode_button)
        self.mode_box.setLayout(self.mode_layout)

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

        # Add widgets to the adc_settings_layout
        self.adc_settings_layout.addWidget(self.start_plot_button)
        self.adc_settings_layout.addWidget(self.adc_sample_rate_box)
        self.adc_settings_layout.addWidget(self.channel_box)
        self.adc_settings_layout.addWidget(self.mode_box)
        self.adc_settings_layout.addWidget(self.time_group)

        # Add the adc_settings_box box to the main layout
        self.main_layout.addWidget(self.adc_settings_box)

        # Create DAC-BRAM settings box
        self.dac_bram_box = QGroupBox("DAC-BRAM Settings")
        self.dac_bram_layout = QHBoxLayout()
        self.dac_bram_box.setLayout(self.dac_bram_layout)

        # Create start button
        self.start_sweep_button = QPushButton("START Sweep")
        self.start_sweep_button.setCheckable(True)
        self.start_sweep_button.setStyleSheet("QPushButton {background-color: green;}")
        self.start_sweep_button.setFixedSize(95, 30)

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
        self.amplitude_edit.setPlaceholderText("Enter Amplitude")

        self.sine_layout.addWidget(self.sine_button)
        self.sine_layout.addWidget(self.amplitude_label)
        self.sine_layout.addWidget(self.amplitude_edit)
        self.signal_layout.addLayout(self.sine_layout)

        self.squareroot_layout = QHBoxLayout()
        self.squareroot_button = QCheckBox("Square Root")
        self.start_voltage_label = QLabel("Start Voltage:")
        self.start_voltage_edit = QLineEdit()
        self.start_voltage_edit.setPlaceholderText("Enter Start V")
        self.stop_voltage_label = QLabel("Stop Voltage:")
        self.stop_voltage_edit = QLineEdit()
        self.stop_voltage_edit.setPlaceholderText("Enter Stop V")
        self.squareroot_layout.addWidget(self.squareroot_button)
        self.squareroot_layout.addWidget(self.start_voltage_label)
        self.squareroot_layout.addWidget(self.start_voltage_edit)
        self.squareroot_layout.addWidget(self.stop_voltage_label)
        self.squareroot_layout.addWidget(self.stop_voltage_edit)
        self.signal_layout.addLayout(self.squareroot_layout)

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

        # Connect signal to slot for checking input validity
        self.amplitude_edit.textChanged.connect(self.validate_amplitude)
        self.start_voltage_edit.textChanged.connect(self.validate_start_voltage)
        self.stop_voltage_edit.textChanged.connect(self.validate_stop_voltage)

        # Add frequency group box to set sample rate of DAC and frequency of signal 
        self.frequency_box = QGroupBox("Frequency setter")
        self.frequency_box_layout = QVBoxLayout()
        self.frequency_box.setLayout(self.frequency_box_layout)

        self.dac_sample_rate_layout = QHBoxLayout()
        self.dac_sample_rate_button = QRadioButton("DAC Sample rate")
        self.dac_sample_rate_button.setChecked(True)
        self.dac_sample_rate_combobox = QComboBox()
        dac_sample_rates = [25, 15.625, 12.5, 7.8125, 6.25, 5, 3.90625, 3.125, 2.5, 1.25, 1, 0.625, 0.5]
        for dac_sample_rate in dac_sample_rates:
            self.dac_sample_rate_combobox.addItem(f"{dac_sample_rate} MHz")
        self.dac_steps_label = QLabel("DAC Steps")
        self.dac_steps_edit = QLineEdit()
        self.dac_steps_edit.setText(str(10))
        self.dwell_time_ms_label = QLabel("Dwell time(ms):")
        self.show_dwell_time_ms_label = QLabel("4e-05")

        self.dac_sample_rate_layout.addWidget(self.dac_sample_rate_button)
        self.dac_sample_rate_layout.addWidget(self.dac_sample_rate_combobox)
        self.dac_sample_rate_layout.addWidget(self.dac_steps_label)
        self.dac_sample_rate_layout.addWidget(self.dac_steps_edit)
        self.dac_sample_rate_layout.addWidget(self.dwell_time_ms_label)
        self.dac_sample_rate_layout.addWidget(self.show_dwell_time_ms_label)

        self.signal_frequency_layout = QHBoxLayout()
        self.signal_frequency_button = QRadioButton("Signal Frequency")
        self.signal_frequency_combobox = QComboBox()
        frequencies = [2.5, 1.25, 625, 500, 312.5, 250, 156.3, 125, 100, 78.1, 62.5, 50, 25, 20, 12.5, 10]
        for MHz_frequency in frequencies[:2]:
            self.signal_frequency_combobox.addItem(f"{MHz_frequency} MHz")
        for KHz_frequencies in frequencies[2:]:
            self.signal_frequency_combobox.addItem(f"{KHz_frequencies} KHz")
        self.max_dac_steps_label = QLabel("Max. DAC steps:")
        self.show_max_dac_steps_label = QLabel("10")

        self.signal_frequency_layout.addWidget(self.signal_frequency_button)
        self.signal_frequency_layout.addWidget(self.signal_frequency_combobox)
        self.signal_frequency_layout.addWidget(self.max_dac_steps_label)
        self.signal_frequency_layout.addWidget(self.show_max_dac_steps_label)

        self.frequency_box_layout.addLayout(self.dac_sample_rate_layout)
        self.frequency_box_layout.addLayout(self.signal_frequency_layout)

        # Add each box to the DAC-BRAM layout
        self.dac_bram_layout.addWidget(self.start_sweep_button)
        self.dac_bram_layout.addWidget(self.signal_box)
        self.dac_bram_layout.addWidget(self.frequency_box)

        # Add the DAC-BRAM group box to the main layout
        self.main_layout.addWidget(self.dac_bram_box)

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
        
        # Connect signals to slots
        self.start_plot_button.clicked.connect(self.start_button_clicked)
        self.adc_sample_rate_combobox.currentIndexChanged.connect(self.update_adc_config)
        self.sync_mode_button.toggled.connect(self.update_adc_config)
        self.async_mode_button.toggled.connect(self.update_adc_config)
        
        self.start_sweep_button.clicked.connect(self.sweep_button_clicked)
        self.sine_button.toggled.connect(self.update_signal_options)
        self.squareroot_button.toggled.connect(self.update_signal_options)
        self.sawtooth_button.toggled.connect(self.update_signal_options)
        self.dac_sample_rate_button.toggled.connect(self.update_frequency_options)
        self.signal_frequency_button.toggled.connect(self.update_frequency_options)
        self.dac_sample_rate_combobox.currentIndexChanged.connect(self.get_frequency_info)
        self.signal_frequency_combobox.currentIndexChanged.connect(self.get_frequency_info)
        self.dac_sample_rate_button.toggled.connect(self.get_frequency_info)
        self.signal_frequency_button.toggled.connect(self.get_frequency_info)
        self.dac_steps_edit.textChanged.connect(self.get_frequency_info)
        self.signal_frequency_combobox.currentIndexChanged.connect(self.set_max_dac_steps)

        # Display settings as soon as the GUI starts
        self.update_signal_options()
        self.update_frequency_options()
        self.display_ram_size()
        self.set_max_dac_steps()

    def toggle_button(self, button, checked_text, unchecked_text, checked_color, unchecked_color):
        
        """" Function to change the color and text of the button upon clicking """

        if button.isChecked():
            button.setText(checked_text)
            button.setStyleSheet(f"QPushButton {{background-color: {checked_color};}}")
        else:
            button.setText(unchecked_text)
            button.setStyleSheet(f"QPushButton {{background-color: {unchecked_color};}}")

    def start_streaming(self, adc_sample_rate, mode, dac_steps, dwell_time_ms):

        """ Start data aquisition and live plot"""

        self.adcreceiver = AdcReceiverThread(adc_sample_rate, mode, dac_steps, dwell_time_ms)
        self.adcreceiver.dataReceived.connect(self.update_plot)
        self.adcreceiver.start()

    @pyqtSlot()
    def start_button_clicked(self):
        self.toggle_button(self.start_plot_button, "STOP Plot", "START Plot", "red", "green")
        if self.start_plot_button.isChecked():
            self.adc_sample_rate, self.mode, self.dac_steps, self.dwell_time_ms = self.get_adc_config()
            self.start_streaming(self.adc_sample_rate, self.mode, self.dac_steps, self.dwell_time_ms)
        else:
            if self.adcreceiver.isRunning():
                self.adcreceiver.terminate()
                self.adcreceiver.wait()
    @pyqtSlot()
    def update_adc_config(self):
        if self.start_plot_button.isChecked():
            if self.adcreceiver.isRunning():
                self.adcreceiver.terminate()
                self.adcreceiver.wait()
            new_adc_sample_rate, new_mode, new_dac_steps, new_dwell_time_ms = self.get_adc_config()
            self.start_streaming(new_adc_sample_rate, new_mode, new_dac_steps, new_dwell_time_ms)


    def start_sweep(self, signal, start_V, stop_V, dac_steps, dwell_time_ms):

        """ Start DAC sweep with after configuring DAC """

        self.dacbramconfigurator = DacBramConfigurator(signal, start_V, stop_V, dac_steps, dwell_time_ms)
        self.dacbramconfigurator.start()
        pita.start_dac_sweep(ALL_BRAM_DAC_PORTS)

    @pyqtSlot()
    def sweep_button_clicked(self):
        self.toggle_button(self.start_sweep_button, "STOP Sweep", "START Sweep", "red", "green")
        if self.start_sweep_button.isChecked():
            signal, start_V, stop_V = self.get_signal_info()
            dac_steps, dwell_time_ms = self.get_frequency_info()
            self.start_sweep(signal, start_V, stop_V, dac_steps, dwell_time_ms)
        else:
            if self.dacbramconfigurator.isRunning():
                self.dacbramconfigurator.terminate()
                self.dacbramconfigurator.wait()
            pita.stop_dac_sweep()

    def get_adc_config(self):

        """
        Get current ADC settings chosen.

        returns
        --------
        adc_sample_rate : float
        mode : string 
        dac_steps : int
        dwell_time_ms : float
        """

        adc_sample_rate = float(self.adc_sample_rate_combobox.currentText().split()[0])
        mode = "Sync" if self.sync_mode_button.isChecked() else "Async"
        dac_steps, dwell_time_ms = self.get_frequency_info() if mode == "Sync" else (0, 0)

        return adc_sample_rate, mode, dac_steps, dwell_time_ms


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
            signal_type = "Sine"
            amplitude = float(self.amplitude_edit.text())
            return signal_type, amplitude, 0   
        else:
            if self.squareroot_button.isChecked():
                signal_type = "Square Root"
                start_V = float(self.start_voltage_edit.text())
                stop_V = float(self.stop_voltage_edit.text())
            else:
                if self.sawtooth_button.isChecked():
                    signal_type = "Sawtooth"
                    start_V = float(self.start_voltage_edit.text())
                    stop_V = float(self.stop_voltage_edit.text())
            return signal_type, start_V, stop_V
        
    def get_frequency_info(self):

        """
        Get dwell time and DAC steps to configure sample rate of DAC.

        returns
        -------
        dac_steps : int
        dwel_time_ms : float 
        """

        dac_steps = int(self.dac_steps_edit.text())
        if self.dac_sample_rate_button.isChecked():
            dac_sample_rate = float(self.dac_sample_rate_combobox.currentText().split()[0])
            dwell_time_ms = 1/(dac_sample_rate*1e3)
        elif self.signal_frequency_button.isChecked():
            signal_frequency = float(self.signal_frequency_combobox.currentText().split()[0])
            if signal_frequency == 2.5 or signal_frequency == 1.25:
                dwell_time_ms = 1/(signal_frequency*1e3*dac_steps)
            else:
                dwell_time_ms = 1/(signal_frequency*dac_steps)
        self.show_dwell_time_ms_label.setText(str(dwell_time_ms))
        return dac_steps, dwell_time_ms
    
    def set_max_dac_steps(self):

        """
        Shows the max. dac steps that can be given when certain signal frequency is desired
        """

        if self.dac_sample_rate_button.isChecked():
            self.dac_steps_edit.setValidator(QIntValidator(0, 2500))
            self.show_max_dac_steps_label.setText(str(2500))
        else:
            signal_frequency = float(self.signal_frequency_combobox.currentText().split()[0])
            if signal_frequency == 2.5 or signal_frequency == 1.25:
                max_dac_steps = int (MHZ_MAX_DAC_FREQ/signal_frequency)
            else:
                max_dac_steps = int (MHZ_MAX_DAC_FREQ/(signal_frequency/1000))

            self.dac_steps_edit.setValidator(QIntValidator(0, max_dac_steps))
            self.show_max_dac_steps_label.setText(str(max_dac_steps))
        

    def display_ram_size(self):
        pass

    # Slots to check if the user input for signal paramerters are valid or not
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

    @pyqtSlot(bytes)
    def update_plot(self, data_raw):
        data = unpackADCData(
            np.frombuffer(data_raw, dtype=np.int32),
            1,
            rawData=False,
        )
        self.y_data_ch1 = data[0] # check .. samples / RAM-Block for 1MB,512KB...
        self.y_data_ch2 = data[1]
        
        total_samples = len(self.y_data_ch1)  # both channels have the same number of samples
        total_time = total_samples / (self.adc_sample_rate * 1e6)  # Convert sample rate from MHz to Hz
        self.x_data = np.linspace(0, total_time, total_samples)

        if self.channel1_button.isChecked():
            self.plot_graph_ch1.setData(self.x_data, self.y_data_ch1)
            self.plot_graph_ch2.clear()

        elif self.channel2_button.isChecked():
            self.plot_graph_ch2.setData(self.x_data, self.y_data_ch2)
            self.plot_graph_ch1.clear()

        else:
            self.plot_graph_ch1.setData(self.x_data, self.y_data_ch1)
            self.plot_graph_ch2.setData(self.x_data, self.y_data_ch2)
            
    def closeEvent(self, event):
        # Ensure the threads are properly terminated
        if hasattr(self, 'adcreceiver') and self.adcreceiver.isRunning():
            self.adcreceiver.terminate()
            self.adcreceiver.wait()
        if hasattr(self, 'dacbramconfigurator') and self.dacbramconfigurator.isRunning():
            self.dacbramconfigurator.terminate()
            self.dacbramconfigurator.wait()
        pita.stop_dac_sweep()
        pita.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
