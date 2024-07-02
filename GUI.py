import sys
import time
import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QCheckBox,
    QHBoxLayout,
    QButtonGroup,
    QComboBox,
    QGroupBox,
    QLabel,
    QApplication,
    QMainWindow,
    QWidget,
    QTabWidget,
    QLineEdit,
)
from rp.adc.helpers import unpackADCData
from rp.ram.config import RAM_SIZE
from AdcReceiver import AdcReceiverThread, pita
from rp.constants import RP_DAC_PORT_1, RP_DAC_PORT_2, ALL_BRAM_DAC_PORTS
from DacBramSettings import StartStopButton, DacBramSettingsTab
from source import stop_sweep
from SignalManager import AdcSignalManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Acquisition in Block Mode")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # default object variables for config:
        self.adc_sample_rate = None
        self.mode = None
        self.adc_sync_dac_steps = None
        self.adc_sync_dac_dwell_time_ms = None
        self.ram_size = None
        self.max_periods = None

        self.adcreceiver = AdcReceiverThread()  # Initialize adcreceiver
        self.adcreceiver.dataReceived.connect(self.update_plot)

        # Create Adc and Dac settings tab with pyqtgraph
        self.create_adc_settings_group()
        self.create_dac_bram_group()
        self.create_plot_widget()
        self.set_max_periods()

        # Initialise AdcSignalManager to connect signals and slots
        self.AdcSignalManager = AdcSignalManager()
        self.AdcSignalManager.connect_signals(self)

    def create_adc_settings_group(self):
        """Create Adc Settings Group in GUI"""

        self.adc_settings_box = QGroupBox("ADC Receiver Settings")
        self.adc_settings_layout = QHBoxLayout(self.adc_settings_box)
        self.main_layout.addWidget(self.adc_settings_box)

        # Add start button
        self.start_plot_button = StartStopButton()
        self.adc_settings_layout.addWidget(self.start_plot_button)

        # Combobox to select Adc Samplerate
        self.adc_sample_rate_box, self.adc_sample_rate_combobox = (
            self.create_combobox_group(
                "ADC Sample Rate",
                [
                    f"{sample_rate} MHz"
                    for sample_rate in [
                        125,
                        62.5,
                        31.25,
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
                ],
            )
        )
        self.adc_settings_layout.addWidget(self.adc_sample_rate_box)

        # Channel checkbox for selecting channel
        self.channel_box, self.channel_layout, self.channel_button_group = (
            self.create_checkbox_group(
                "Channel Selection",
                ["Channel 1", "Channel 2", "Both"],
                default_checked="Channel 1",
            )
        )
        self.adc_settings_layout.addWidget(self.channel_box)

        # Mode checkbox to select either sync or async mode
        self.mode_box, self.mode_layout, self.mode_button_group = (
            self.create_checkbox_group(
                "ADC Mode", ["Async", "Sync"], default_checked="Sync"
            )
        )

        self.sync_mode_button = self.mode_button_group.buttons()[1]
        self.adc_settings_layout.addWidget(self.mode_box)

        # Select RAM-Size
        self.ram_size_box, self.ram_size_combobox = self.create_combobox_group(
            "RAM Size in KB", [f"{size}" for size in [512, 256, 128, 64]]
        )
        self.adc_settings_layout.addWidget(self.ram_size_box)

        # Groupbox to Set the number of periods and to show total periods
        self.periods_box = QGroupBox("Periods Settings")
        self.periods_box.setFixedWidth(400)
        self.periods_box_layout = QVBoxLayout(self.periods_box)
        self.input_periods_layout = QHBoxLayout()
        self.show_periods_layout = QHBoxLayout()

        self.periods_label = QLabel("Set Periods:")
        self.periods_edit = QLineEdit()
        self.periods_edit.setText(str(1000))
        self.periods_edit.setValidator(QDoubleValidator())
        self.max_periods_label = QLabel("Max Periods:")
        self.show_max_periods_label = QLabel(str(self.max_periods))

        self.input_periods_layout.addWidget(self.periods_label)
        self.input_periods_layout.addWidget(self.periods_edit)

        self.show_periods_layout.addWidget(self.max_periods_label)
        self.show_periods_layout.addWidget(self.show_max_periods_label)

        self.periods_box_layout.addLayout(self.input_periods_layout)
        self.periods_box_layout.addLayout(self.show_periods_layout)

        self.adc_settings_layout.addWidget(self.periods_box)

    def create_dac_bram_group(self):
        """Integrate DacBramSettingsTab into the GUI"""

        self.dac_bram_group_box = QGroupBox("DAC BRAM Settings")
        self.group_layout = QVBoxLayout(self.dac_bram_group_box)
        self.main_layout.addWidget(self.dac_bram_group_box)

        self.tab_widget = QTabWidget()
        self.group_layout.addWidget(self.tab_widget)

        self.tab1 = DacBramSettingsTab(self.adcreceiver, channel=0)
        self.tab2 = DacBramSettingsTab(self.adcreceiver, channel=1)

        self.tab_widget.addTab(self.tab1, "PORT0")
        self.tab_widget.addTab(self.tab2, "PORT1")

    def create_plot_widget(self):
        """Create pyqtgraph to plot the data"""

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(True, True)
        self.plot_widget.setLabel("left", "Voltage", units="V")
        self.plot_widget.setLabel("bottom", "time", units="s")
        self.plot_widget.addLegend()

        self.x_data = np.zeros(1000)
        self.y_data_ch1 = np.zeros(1000)
        self.plot_graph_ch1 = self.plot_widget.plot(
            self.x_data, self.y_data_ch1, pen="r", name="Channel 1"
        )
        self.y_data_ch2 = np.zeros(1000)
        self.plot_graph_ch2 = self.plot_widget.plot(
            self.x_data, self.y_data_ch2, pen="b", name="Channel 2"
        )

        self.main_layout.addWidget(self.plot_widget, stretch=1)

    def create_combobox_group(self, title, items):
        group_box = QGroupBox(title)
        layout = QVBoxLayout(group_box)
        combobox = QComboBox()
        for item in items:
            combobox.addItem(item)
        layout.addWidget(combobox)
        return group_box, combobox

    def create_checkbox_group(self, title, items, default_checked=None):
        group_box = QGroupBox(title)
        layout = QVBoxLayout(group_box)
        button_group = QButtonGroup(self)
        for item in items:
            checkbox = QCheckBox(item)
            if item == default_checked:
                checkbox.setChecked(True)
            button_group.addButton(checkbox)
            layout.addWidget(checkbox)
        return group_box, layout, button_group
    
    @pyqtSlot()
    def start_button_clicked(self):
        self.start_plot_button.toggle_button()
        if self.start_plot_button.isChecked():
            self.get_adc_config()
            self.adcreceiver.set_parameters(
                self.adc_sample_rate,
                self.mode,
                self.adc_sync_dac_steps,
                self.adc_sync_dac_dwell_time_ms,
                self.ram_size,
                )
            self.adcreceiver.start()
        else:
            self.adcreceiver.stop()

    @pyqtSlot()
    def update_adc_config(self):
        if self.start_plot_button.isChecked():
            self.restart_adc_receiver()

    def get_adc_config(self):
        self.adc_sample_rate = float(
            self.adc_sample_rate_combobox.currentText().split()[0]
        )
        self.mode = "Sync" if self.sync_mode_button.isChecked() else "Async"
        self.adc_sync_dac_steps, self.adc_sync_dac_dwell_time_ms = (
            self.tab1.dac_steps,
            self.tab1.dwell_time_ms,
        )
        self.get_ram_size()

    def get_ram_size(self):
        """Get the selected RAM-size"""

        ram_sizes = ["KB_512", "KB_256", "KB_128", "KB_64"]
        selected_index = self.ram_size_combobox.currentIndex()
        selected_ram_size = ram_sizes[selected_index] 
        self.ram_size = RAM_SIZE[selected_ram_size]

    def set_max_periods(self):
        """ Shows the max. number of Periods """
        self.get_adc_config()
        ram = int(self.ram_size_combobox.currentText())
        self.max_periods = (ram * 1024 / 4) / ((self.adc_sync_dac_steps * self.adc_sync_dac_dwell_time_ms * 1e3) * self.adc_sample_rate)
        self.show_max_periods_label.setText(str(self.max_periods))

    @pyqtSlot(bytes)
    def update_plot(self, data_raw):
        data = unpackADCData(np.frombuffer(data_raw, dtype=np.int32), 1, rawData=False)
        self.y_data_ch1, self.y_data_ch2 = data[0], data[1]

        total_samples = len(self.y_data_ch1)
        total_time = total_samples / (self.adc_sample_rate * 1e6)
        self.x_data = np.linspace(0, total_time, total_samples)

        if self.channel_button_group.buttons()[0].isChecked():  # Channel 1
            self.plot_graph_ch1.setData(self.x_data, self.y_data_ch1)
            self.plot_graph_ch2.clear()
        elif self.channel_button_group.buttons()[1].isChecked():  # Channel 2
            self.plot_graph_ch2.setData(self.x_data, self.y_data_ch2)
            self.plot_graph_ch1.clear()
        else:
            self.plot_graph_ch1.setData(self.x_data, self.y_data_ch1)
            self.plot_graph_ch2.setData(self.x_data, self.y_data_ch2)

    def closeEvent(self, event):
        if self.adcreceiver.isRunning():
            self.adcreceiver.stop()
            self.adcreceiver.deleteLater()

        # reset_voltage_port1 = self.tab1.get_reset_voltage()
        # reset_voltage_port2 = self.tab2.get_reset_voltage()

        # stop_sweep(pita, RP_DAC_PORT_1, reset_voltage_port1)
        # stop_sweep(pita, RP_DAC_PORT_2, reset_voltage_port2)
        pita.stop_dac_sweep(port=ALL_BRAM_DAC_PORTS)
        pita.close()

        event.accept()

    def restart_adc_receiver(self):
        if self.adcreceiver.isRunning():
            self.adcreceiver.stop()
        time.sleep(0.1)

        self.get_adc_config()
        self.adcreceiver.set_parameters(
            self.adc_sample_rate,
            self.mode,
            self.adc_sync_dac_steps,
            self.adc_sync_dac_dwell_time_ms,
            self.ram_size,
        )
        self.adcreceiver.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
