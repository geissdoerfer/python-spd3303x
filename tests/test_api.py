import pytest
import pyvisa
import vxi11
import socket

from spd3303x import SPD3303X

def fakegethostbyname(host):
    return "192.168.0.4"

class FakeInstrument(object):
    def __init__(self):
        self.last_cmd = None

    def write(self, cmd):
        self.last_cmd = cmd

    def close(self):
        pass

class FakeVisaInstrument(FakeInstrument):
    def __init__(self):
        self.read_termination = ""
        self.write_termination = ""
        super().__init__()

    def read(self):
        return "Siglent Technologies,SPD3303X,SPD3XIDQ4R3481,1.01.01.02.05,V3.0"


class FakeVXIInstrument(FakeInstrument):
    def __init__(self, ip_addr):
        super().__init__()

    def ask(self, cmd):
        self.write(cmd)
        return "Siglent Technologies,SPD3303X,SPD3XIDQ4R3481,1.01.01.02.05,V3.0"



class FakeVisaResourceManager(object):
    def __init__(self, *arg):
        pass

    def open_resource(self, rscr_str):
        return FakeVisaInstrument()

    def list_resources(self):
        return ('USB0::1155::30016::SPD3XIDQ4R3481::0::INSTR',)


def test_instantiation_visa(monkeypatch):
    monkeypatch.setattr(pyvisa, "ResourceManager", FakeVisaResourceManager)
    with SPD3303X.usb_device() as dev:
        assert dev._inst.last_cmd == "*IDN?"
    with SPD3303X.usb_device("USB0::1510::9732::???::0::INSTR") as dev:
        assert dev._inst.last_cmd == "*IDN?"

def test_instantiation_vxi(monkeypatch):
    monkeypatch.setattr(vxi11, "Instrument", FakeVXIInstrument)
    monkeypatch.setattr(socket, "gethostbyname", fakegethostbyname)

    with SPD3303X.ethernet_device("192.168.0.4") as dev:
        assert dev._inst.last_cmd == "*IDN?"

@pytest.fixture(params=["usb", "ethernet"])
def device(request, monkeypatch):
    if request.param == "usb":
        monkeypatch.setattr(pyvisa, "ResourceManager", FakeVisaResourceManager)
        with SPD3303X.usb_device() as dev:
            yield dev
    elif request.param == "ethernet":
        monkeypatch.setattr(vxi11, "Instrument", FakeVXIInstrument)
        monkeypatch.setattr(socket, "gethostbyname", fakegethostbyname)
        with SPD3303X.ethernet_device("anyhost.local") as dev:
            yield dev
    else:
        raise Exception(f"Unknown connection type {conn_type}")

@pytest.fixture(params=["CH1", "CH2", "CH3"])
def channel_name(request):
    return request.param

@pytest.fixture
def channel(device, channel_name):
    yield getattr(device, channel_name)

@pytest.fixture(params=["CH1", "CH2"])
def var_channel_name(request):
    return request.param

@pytest.fixture()
def fixed_channel_name(request):
    return "CH3"

@pytest.fixture()
def var_channel(device, var_channel_name):
    yield getattr(device, var_channel_name)

@pytest.fixture
def fixed_channel(device, fixed_channel_name):
    yield getattr(device, fixed_channel_name)

def test_write(device):
    device.write("some command")
    assert device._inst.last_cmd == "some command"

def test_query(device):
    assert device.query("*IDN?") == "Siglent Technologies,SPD3303X,SPD3XIDQ4R3481,1.01.01.02.05,V3.0"

def test_onoff(channel):
    channel.set_output(True)
    channel.set_output(False)

def test_set_fail(fixed_channel):
    with pytest.raises(Exception):
        fixed_channel.set_voltage(3.0)
    with pytest.raises(Exception):
        fixed_channel.set_current(1.0)

def test_set(device, var_channel_name, var_channel):
    var_channel.set_voltage(3.0)
    assert device._inst.last_cmd == f"{var_channel_name}:VOLT 3.000"
    var_channel.set_current(1.0)
    assert device._inst.last_cmd == f"{var_channel_name}:CURR 1.000"
