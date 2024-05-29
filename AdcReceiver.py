from PyQt6.QtCore import QThread, pyqtSignal
import time

from rp.core import RedPitayaBoard
from source import *
from rp.constants import ALL_BRAM_DAC_PORTS

VERBOSE = False

class AdcReceiverThread(QThread):
    dataReceived = pyqtSignal(bytes)
    pita = RedPitayaBoard(verbose = VERBOSE)

    def __init__(self, sample_rate, signal, start_V, stop_V):
        super().__init__()
        self.running = False
        self.sample_rate = sample_rate
        self.signal = signal
        self.start_V = start_V
        self.stop_V = stop_V

    def run(self):
        self.running = True
        self.config = initMeasurement(self.pita, self.sample_rate, self.signal, self.start_V, self.stop_V,VERBOSE)
        self.number_tcp_pkg = self.config["adc"]["tcp"]
        self.tcp_pkg_size_bytes = self.config["ram"].tcp_pkg_size_bytes
        self.pita.start_dac_sweep(port = ALL_BRAM_DAC_PORTS)
        
        while self.running:
                self.pita.start_adc_sampling(self.number_tcp_pkg)
                index = 0
                while index < self.number_tcp_pkg:
                    receive_start = time.time()
                    data_raw = self.pita.receive_adc_data_package(2*int(self.tcp_pkg_size_bytes))
                    receive_end = time.time()
                    print(f"Data received in {receive_end-receive_start} s")
                    self.dataReceived.emit(data_raw)
                    index += 2
                    time.sleep(0.1)
