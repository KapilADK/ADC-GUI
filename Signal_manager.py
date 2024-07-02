from PyQt6.QtCore import QObject


class DacSignalManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    def connect_signals(self, widget):
        widget.start_sweep_button.clicked.connect(widget.sweep_button_clicked)

        widget.sine_button.clicked.connect(widget.update_signal_options)
        widget.squareroot_button.clicked.connect(widget.update_signal_options)
        widget.sawtooth_button.clicked.connect(widget.update_signal_options)

        widget.dac_sample_rate_button.toggled.connect(widget.update_frequency_options)

        widget.dac_sample_rate_button.toggled.connect(widget.set_max_dac_steps)

        widget.dac_sample_rate_combobox.currentIndexChanged.connect(
            widget.get_frequency_info
        )
        widget.dac_sample_rate_button.toggled.connect(widget.get_frequency_info)
        widget.signal_frequency_combobox.currentIndexChanged.connect(
            widget.get_frequency_info
        )
        widget.dac_steps_edit.textChanged.connect(widget.get_frequency_info)

        widget.signal_frequency_combobox.currentIndexChanged.connect(
            widget.set_max_dac_steps
        )
        widget.dac_steps_edit.textChanged.connect(widget.validate_dac_steps)
        widget.dac_sample_rate_button.toggled.connect(
            widget.validate_dac_steps_upon_button_toggled
        )
        widget.signal_frequency_combobox.currentIndexChanged.connect(
            widget.validate_dac_steps_upon_button_toggled
        )

        # SIgnals that when emitted should configure the BRAM again
        widget.sine_button.clicked.connect(widget.update_dac_config)
        widget.squareroot_button.clicked.connect(widget.update_dac_config)
        widget.sawtooth_button.clicked.connect(widget.update_dac_config)
        widget.amplitude_edit.returnPressed.connect(widget.update_dac_config)
        widget.start_voltage_edit.returnPressed.connect(widget.update_dac_config)
        widget.stop_voltage_edit.returnPressed.connect(widget.update_dac_config)
        widget.dac_sample_rate_combobox.currentIndexChanged.connect(
            widget.update_dac_config
        )
        widget.dac_steps_edit.returnPressed.connect(widget.update_dac_config)
        widget.signal_frequency_combobox.currentIndexChanged.connect(
            widget.update_dac_config
        )
        widget.dac_sample_rate_button.toggled.connect(widget.update_dac_config)


class AdcSignalManager(QObject):
    def __init__(self):
        super().__init__()

    def connect_signals(self, widget):
        widget.start_plot_button.clicked.connect(widget.start_button_clicked)

        # Signals that when emitted should configure the AdcReceiver again
        widget.adc_sample_rate_combobox.currentIndexChanged.connect(
            widget.update_adc_config
        )
        widget.sync_mode_button.toggled.connect(widget.update_adc_config)
        widget.ram_size_combobox.currentIndexChanged.connect(widget.update_adc_config)
        widget.tab1.update_adc.connect(widget.update_adc_config)
        widget.tab2.update_adc.connect(widget.update_adc_config)
        widget.ram_size_combobox.currentIndexChanged.connect(widget.set_max_periods)
        widget.adc_sample_rate_combobox.currentIndexChanged.connect(widget.set_max_periods)
        widget.tab1.dac_sample_rate_button.toggled.connect(widget.set_max_periods)
        widget.tab1.dac_sample_rate_combobox.currentIndexChanged.connect(widget.set_max_periods)
        widget.tab1.dac_steps_edit.returnPressed.connect(widget.set_max_periods)
        widget.tab1.signal_frequency_combobox.currentIndexChanged.connect(widget.set_max_periods)
        #widget.periods_edit.returnPressed.connect(widget.update_plot)
