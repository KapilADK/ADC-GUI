from PyQt6.QtCore import QObject

class SignalManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def connect_signals(self, widget):
        widget.start_sweep_button.clicked.connect(widget.sweep_button_clicked)
        widget.sine_button.toggled.connect(widget.update_signal_options)
        widget.squareroot_button.toggled.connect(widget.update_signal_options)

        widget.dac_sample_rate_button.toggled.connect(widget.update_frequency_options)
        widget.dac_sample_rate_button.toggled.connect(widget.get_frequency_info)
        widget.dac_sample_rate_button.toggled.connect(widget.set_max_dac_steps)
        widget.dac_sample_rate_combobox.currentIndexChanged.connect(widget.get_frequency_info)
        widget.signal_frequency_combobox.currentIndexChanged.connect(widget.get_frequency_info)
        widget.signal_frequency_combobox.currentIndexChanged.connect(widget.set_max_dac_steps)
        widget.dac_steps_edit.textChanged.connect(widget.get_frequency_info)
        widget.dac_steps_edit.textChanged.connect(widget.validate_dac_steps)
        widget.dac_sample_rate_button.toggled.connect(widget.validate_dac_steps_upon_button_toggled)
        widget.signal_frequency_combobox.currentIndexChanged.connect(widget.validate_dac_steps_upon_button_toggled)

        widget.sine_button.toggled.connect(widget.update_dac_config)
        widget.squareroot_button.toggled.connect(widget.update_dac_config)
        widget.sawtooth_button.toggled.connect(widget.update_dac_config)
        widget.amplitude_edit.returnPressed.connect(widget.update_dac_config)
        widget.start_voltage_edit.returnPressed.connect(widget.update_dac_config)
        widget.stop_voltage_edit.returnPressed.connect(widget.update_dac_config)
        widget.dac_sample_rate_combobox.currentIndexChanged.connect(widget.update_dac_config)
        widget.dac_steps_edit.returnPressed.connect(widget.update_dac_config)
        widget.signal_frequency_combobox.currentIndexChanged.connect(widget.update_dac_config)
        widget.dac_sample_rate_button.toggled.connect(widget.update_dac_config)
#Dac_BramSettings

 # Initialize and use the SignalManager
        self.signal_manager = SignalManager()
        self.signal_manager.connect_signals(self)
