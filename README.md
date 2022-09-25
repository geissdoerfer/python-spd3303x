[![PyPiVersion](https://img.shields.io/pypi/v/spd3303x.svg)](https://pypi.org/project/spd3303x)
[![Pytest](https://github.com/geissdoerfer/python-spd3303x/actions/workflows/python-tests.yml/badge.svg)](https://github.com/geissdoerfer/python-spd3303x/actions/workflows/python-tests.yml)
[![CodeStyle](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


# Introduction

Siglent SPD3303X/-E are programmable lab bench power supplies.
They can be accessed remotely via a VISA interface.

This package provides a python API for convenient remote programming of the Device via Ethernet/USB.
Currently, the module supports setting voltage and current limits, measuring voltage and current and enabling or disabling individual outputs.

The module also provides a CLI tool to conveniently control the power supply from the command line.

Also supports the very similar RS PRO RSPD3303X-E.

# Installation

The package is hosted on PyPI. Install it with

```
pip install spd3303x
```

or

```
pipenv install spd3303x
```

# Examples

To connect to a device that is connected to a LAN and accessible under IP `192.168.0.4`:

```python
with SPD3303X.ethernet_device("192.168.0.4") as dev:
    dev.CH1.set_voltage(8)
    dev.CH1.set_current(0.75)
    dev.CH1.set_output(True)
    print(dev.CH1.get_current())
    print(dev.CH1.get_voltage())
    print(dev.CH1.measure_voltage())
    print(dev.CH1.measure_current())
    dev.CH3.set_output(True)
```

To connect to a USB device:

```python
with SPD3303X.usb_device() as dev:
    dev.CH1.set_voltage(8)
    dev.CH1.set_current(0.75)
    dev.CH1.set_output(True)
    print(dev.CH1.get_current())
    print(dev.CH1.get_voltage())
    print(dev.CH1.measure_voltage())
    print(dev.CH1.measure_current())
    dev.CH3.set_output(True)
```

# CLI

To configure and enable channel 1 on an ethernet device under IP `192.168.0.4`:

```
spd-ctrl -d 192.168.0.4 set 1 --voltage 3.3 --current 0.5 --on
```

To configure channel 2 on a USB device:

```
spd-ctrl set 2 -v 5 -c 0.1
```

To disable (fixed) channel 3 on a USB device with verbose logging:

```
spd-ctrl -vvv set 3 --off
```

To list all available options try:

```
spd-ctrl --help
spd-ctrl set --help
```
