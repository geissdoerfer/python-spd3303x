import pyvisa
import numpy as np
import time
import xdrlib
import logging
import socket
import vxi11

consoleHandler = logging.StreamHandler()
logger = logging.getLogger("spd3303x")
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)

class SPD3303X(object):

    KNOWN_MODELS = [
        "SPD3303X",
        "SPD3303X-E",
        "SPD3XIDD5R7170",
    ]

    MANUFACTURERS = {
        "SPD3303X": "Siglent",
        "SPD3303X-E": "Siglent",
        # This one is called RSPD3303X-E by RS PRO.
        "SPD3XIDD5R7170": "[RS PRO]",
    }


    @classmethod
    def usb_device(cls, visa_rscr: str=None):
        return USBDevice(visa_rscr)

    @classmethod
    def ethernet_device(cls, host: str):
        return EthernetDevice(host)

    class Channel(object):
        def __init__(self, chan_no: int, dev):
            self._name = f"CH{chan_no}"
            self._dev = dev

        def set_output(self, status: bool):
            self._dev.write(f"OUTP {self._name},{'ON' if status else 'OFF'}")

    class ControlledChannel(Channel):
        def set_voltage(self, voltage: float):
            self._dev.write(f"{self._name}:VOLT {voltage:.3f}")

        def set_current(self, current: float):
            self._dev.write(f"{self._name}:CURR {current:.3f}")

        def get_voltage(self):
            return self._dev.query(f"{self._name}:VOLT?")

        def get_current(self):
            return self._dev.query(f"{self._name}:CURR?")

        def measure_voltage(self):
            return self._dev.query(f"MEAS:VOLT? {self._name}")

        def measure_current(self):
            return self._dev.query(f"MEAS:CURR? {self._name}")

        def measure_power(self):
            return self._dev.query(f"MEAS:POWE? {self._name}")

    def __enter__(self):
        try:
            dsc = self.query("*IDN?")
        except pyvisa.errors.VisaIOError:
            self._inst.close()
            raise
        identity_items = dsc.split(",")
        if len(identity_items) == 3:
            # RS PRO RSPD3303X-E ?
            model, _, _= dsc.split(",")
            mnf = self.MANUFACTURERS.get(model, "[Unknown]")
        else:
            # Proper Siglent device probably.
            mnf, model,_,_,_ = identity_items
        logger.debug(f"Discovered {model} by {mnf}")
        if model not in self.KNOWN_MODELS:
            raise Exception(f"Device {model} not supported")
        self.CH1 = SPD3303X.ControlledChannel(1, self)
        self.CH2 = SPD3303X.ControlledChannel(2, self)
        self.CH3 = SPD3303X.Channel(3, self)
        return self

    def __exit__(self, *args):
        self._inst.close()

class USBDevice(SPD3303X):
    def __init__(self, visa_rscr: str=None):
        self._visa_rscr = visa_rscr

    def __enter__(self):
        rm = pyvisa.ResourceManager("@py")
        if self._visa_rscr is None:
            logger.debug("Trying to auto-detect USB device")
            resources = rm.list_resources()
            for res_str in resources:
                if "SPD3XID" in res_str:
                    self._visa_rscr = res_str
            if self._visa_rscr is None:
                raise Exception("No device found")

        self._inst = rm.open_resource(self._visa_rscr)
        self._inst.write_termination="\n"
        self._inst.read_termination="\n"
        return super().__enter__()

    def write(self, cmd: str):
        self._inst.write(cmd)
        time.sleep(0.1)

    def query(self, cmd: str):
        self.write(cmd)
        rep = self._inst.read()
        time.sleep(0.1)
        return rep

class EthernetDevice(SPD3303X):
    def __init__(self, host: str):
        self._host = host

    def __enter__(self):
        try:
            logger.debug(f"Trying to resolve host {self._host}")
            ip_addr = socket.gethostbyname(self._host)
        except socket.gaierror:
            logger.error(f"Couldn't resolve host {self._host}")

        self._inst = vxi11.Instrument(ip_addr)
        return super().__enter__()

    def write(self, cmd: str):
        self._inst.write(cmd)
        time.sleep(0.1)

    def query(self, cmd: str):
        return self._inst.ask(cmd)

