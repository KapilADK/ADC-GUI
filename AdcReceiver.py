from PyQt6.QtCore import QThread, pyqtSignal
import time

from rp.core import RedPitayaBoard
from source import initAdcReceiver

DEBUG_MODE = False
VERBOSE = False
autoStartServer = False

pita = RedPitayaBoard(
    debug=DEBUG_MODE, verbose=VERBOSE, autoStartServer=autoStartServer
)

class AdcReceiverThread(QThread):
    dataReceived = pyqtSignal(bytes)

    def __init__(self):
        super().__init__()
        self.running = False
        self.sample_rate = None
        self.mode = None
        self.dac_steps = None
        self.dwell_time_ms = None

    def set_parameters(self, sample_rate, mode, dac_steps, dwell_time_ms):
        self.sample_rate, self.mode, self.dac_steps, self.dwell_time_ms = (
            sample_rate, mode, dac_steps, dwell_time_ms
        )

    def run(self):
        self.running = True
        self.config_adc = initAdcReceiver(
            pita,
            self.sample_rate,
            self.mode,
            self.dac_steps,
            self.dwell_time_ms,
            VERBOSE,
        )
        self.number_tcp_pkg = self.config_adc["adc"]["tcp"]
        self.tcp_pkg_size_bytes = self.config_adc["ram"].tcp_pkg_size_bytes

        while self.running:
            pita.start_adc_sampling(self.number_tcp_pkg)
            index = 0
            while index < self.number_tcp_pkg:
                data_raw = pita.receive_adc_data_package(
                    2 * int(self.tcp_pkg_size_bytes)
                )
                self.dataReceived.emit(data_raw)
                index += 2
                time.sleep(0.1)

    def stop(self):
        self.running = False
        self.wait()
