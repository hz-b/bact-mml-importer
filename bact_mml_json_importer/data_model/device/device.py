from dataclasses import dataclass

from .control_system_access import ControlSystemSignal
from .conversion_info import ConversionInfo
from .limits import Limits


@dataclass
class UnitNames:
    hardware: str
    physics: str


@dataclass
class InfoCommChannel:
    info: ConversionInfo
    comm: ControlSystemSignal


@dataclass
class DeviceInfo:
    unit_names: UnitNames
    limits: Limits
    setpoint: InfoCommChannel
    monitor: InfoCommChannel
