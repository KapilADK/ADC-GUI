from PyQt6.QtCore import QObject


class DacSignalManager(QObject):
    def __init__(self):
        super().__init__()

    def connect_signals(self, widget):
        widget.start_sweep_button.clicked.connect(widget.sweep_button_clicked)

        widget.dac_steps_edit.textChanged.connect(widget.validate_dac_steps)

        # Signals that when emitted should configure the BRAM again
        widget.sine_button.clicked.connect(widget.update_dac_config)
        widget.squareroot_button.clicked.connect(widget.update_dac_config)
        widget.sawtooth_button.clicked.connect(widget.update_dac_config)
        widget.amplitude_edit.returnPressed.connect(widget.update_dac_config)
        widget.start_voltage_edit.returnPressed.connect(widget.update_dac_config)
        widget.stop_voltage_edit.returnPressed.connect(widget.update_dac_config)
        widget.dac_sample_rate_combobox.currentIndexChanged.connect(
            widget.update_dac_config
        )
        widget.dac_steps_edit.returnPressed.connect(widget.show_signal_frequency)
        widget.dac_steps_edit.returnPressed.connect(widget.update_dac_config)
        widget.signal_frequency_combobox.currentIndexChanged.connect(
            widget.update_dac_config
        )
        widget.dac_sample_rate_button.clicked.connect(widget.update_dac_config)
        widget.signal_frequency_button.clicked.connect(widget.show_signal_frequency)

class AdcSignalManager(QObject):
    def __init__(self):
        super().__init__()

    def connect_signals(self, widget):
        widget.start_plot_button.clicked.connect(widget.start_button_clicked)
        widget.periods_edit.textChanged.connect(widget.validate_periods)
        widget.periods_edit.returnPressed.connect(widget.get_samples_to_plot)
        widget.channel_button_group.buttons()[0].clicked.connect(widget.enableAutoRange)
        widget.channel_button_group.buttons()[1].clicked.connect(widget.enableAutoRange)
        widget.channel_button_group.buttons()[2].clicked.connect(widget.enableAutoRange)
        # Signals that when emitted should configure the AdcReceiver again
        widget.adc_sample_rate_combobox.currentIndexChanged.connect(
            widget.update_adc_config
        )
        widget.mode_button_group.buttons()[0].clicked.connect(widget.update_adc_config)
        widget.mode_button_group.buttons()[1].clicked.connect(widget.update_adc_config)
        widget.ram_size_combobox.currentIndexChanged.connect(widget.update_adc_config)
        widget.tab1.update_adc.connect(widget.update_adc_config)
        widget.tab2.update_adc.connect(widget.update_adc_config)
