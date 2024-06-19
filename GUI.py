import sys
import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import (
    QVBoxLayout, QCheckBox, QHBoxLayout, QButtonGroup, QComboBox, QGroupBox,
    QLabel, QApplication, QMainWindow, QWidget, QTabWidget
)
from rp.adc.helpers import unpackADCData
from AdcReceiver import AdcReceiverThread, pita
from rp.constants import RP_DAC_PORT_1, RP_DAC_PORT_2, ALL_BRAM_DAC_PORTS
from DacBramSettings import StartStopButton, DacBramSettingsTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Acquisition in Block Mode")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.adc_sample_rate = None
        self.mode = None
        self.dac_steps = None
        self.dwell_time_ms = None

        self.adcreceiver = AdcReceiverThread()  # Initialize adcreceiver here
        self.adcreceiver.dataReceived.connect(self.update_plot)

        self.create_adc_settings_group()
        self.create_dac_bram_group()
        self.create_plot_widget()

        self.start_plot_button.clicked.connect(self.start_button_clicked)
        self.adc_sample_rate_combobox.currentIndexChanged.connect(self.update_adc_config)
        self.sync_mode_button.toggled.connect(self.update_adc_config)

    def create_adc_settings_group(self):
        self.adc_settings_box = QGroupBox("ADC Receiver Settings")
        self.adc_settings_layout = QHBoxLayout(self.adc_settings_box)
        self.main_layout.addWidget(self.adc_settings_box)

        self.start_plot_button = StartStopButton()
        self.adc_settings_layout.addWidget(self.start_plot_button)

        self.adc_sample_rate_box, self.adc_sample_rate_combobox = self.create_combobox_group(
            "ADC Sample Rate", [f"{sr} MHz" for sr in [125, 62.5, 31.25, 25, 15.625, 12.5, 7.8125, 6.25, 5, 3.90625, 3.125, 2.5, 1.25, 1, 0.625, 0.5]]
        )
        self.adc_settings_layout.addWidget(self.adc_sample_rate_box)

        self.channel_box, self.channel_layout, self.channel_button_group = self.create_checkbox_group(
            "Channel Selection", ["Channel 1", "Channel 2", "Both"]
        )
        self.adc_settings_layout.addWidget(self.channel_box)

        self.mode_box, self.mode_layout, self.mode_button_group = self.create_checkbox_group(
            "ADC Mode", ["Async", "Sync"], default_checked="Sync"
        )
        self.sync_mode_button = self.mode_button_group.buttons()[1]  # Sync button
        self.adc_settings_layout.addWidget(self.mode_box)

        self.time_group, self.time_menu = self.create_combobox_group(
            "Time to write RAM in ms", [f"{time} ms" for time in [10, 20, 50, 100, 200]]
        )
        self.output_ram_size = QLabel()
        self.output_ram_size_layout = QHBoxLayout()
        self.output_ram_size_layout.addWidget(QLabel("RAM Size:"))
        self.output_ram_size_layout.addWidget(self.output_ram_size)
        self.time_group.layout().addLayout(self.output_ram_size_layout)
        self.adc_settings_layout.addWidget(self.time_group)

    def create_dac_bram_group(self):
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
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(True, True)
        self.plot_widget.setLabel("left", "Voltage", units="V")
        self.plot_widget.setLabel("bottom", "time", units="s")
        self.plot_widget.addLegend()

        self.x_data = np.zeros(1000)
        self.y_data_ch1 = np.zeros(1000)
        self.plot_graph_ch1 = self.plot_widget.plot(self.x_data, self.y_data_ch1, pen="r", name="Channel 1")
        self.y_data_ch2 = np.zeros(1000)
        self.plot_graph_ch2 = self.plot_widget.plot(self.x_data, self.y_data_ch2, pen="b", name="Channel 2")

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
            self.adcreceiver.set_parameters(self.adc_sample_rate, self.mode, self.dac_steps, self.dwell_time_ms)
            self.adcreceiver.start()
        else:
            self.adcreceiver.stop()

    @pyqtSlot()
    def update_adc_config(self):
        if self.start_plot_button.isChecked():
            self.restart_adc_receiver()

    def get_adc_config(self):
        self.adc_sample_rate = float(self.adc_sample_rate_combobox.currentText().split()[0])
        self.mode = "Sync" if self.sync_mode_button.isChecked() else "Async"
        self.dac_steps, self.dwell_time_ms = self.tab1.get_frequency_info()

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
            self.adcreceiver.terminate()
            self.adcreceiver.stop()

        reset_voltage_port1 = self.tab1.get_reset_voltage()
        reset_voltage_port2 = self.tab2.get_reset_voltage()

        pita.stop_dac_sweep(port=ALL_BRAM_DAC_PORTS)
        pita.set_voltage_rp_dac(RP_DAC_PORT_1, reset_voltage_port1)
        pita.set_voltage_rp_dac(RP_DAC_PORT_2, reset_voltage_port2)

        pita.close()
        event.accept()

    def restart_adc_receiver(self):
        if self.adcreceiver.isRunning():
            self.adcreceiver.stop()
        self.get_adc_config()
        self.adcreceiver.set_parameters(self.adc_sample_rate, self.mode, self.dac_steps, self.dwell_time_ms)
        self.adcreceiver.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
