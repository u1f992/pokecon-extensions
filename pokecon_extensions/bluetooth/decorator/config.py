from __future__ import annotations
import glob

import platform

from pydantic import BaseModel, validator
from serial import Serial, SerialException

from ..session import ControllerColor


def _list_ports():
    """
    https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
    """
    if platform.system() == "Windows":
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif platform.system() == "Darwin":
        ports = glob.glob('/dev/tty.*')
    elif platform.system() == "Linux":
        ports = glob.glob('/dev/tty[A-Za-z]*')
    else:
        raise EnvironmentError('Unsupported platform')

    result: list[str] = []
    for port in ports:
        try:
            s = Serial(port)
            s.close()
            result.append(port)
        except (OSError, SerialException):
            pass
    return result


class Config(BaseModel):
    port: str
    baudrate: int
    timeout: int
    conrtoller_color: ControllerColor = ControllerColor()

    @validator("port")
    def port_must_exist(cls, value: str):
        assert value in _list_ports()
        return value

    @validator("baudrate")
    def baudrate_must_be_one_of(cls, value: int):
        assert value in [50, 75, 110, 134, 150, 200, 300, 600,
                         1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
        return value

    @validator("timeout")
    def timeout_must_be_positive(cls, value: int):
        assert 0 <= value
        return value
