from enum import Enum
from typing import Optional, Sequence

from attr import dataclass


class MachineType(Enum):
    storage_ring = "StorageRing"


@dataclass(frozen=True)
class DesignInfo:
    """
    Todo: what is this precisly
    """

    energy: float
    injection_energy: float
    harmonic_number: int
    length: float


@dataclass(frozen=True)
class AdjustmentInfo:
    #: what's that seems to be r
    delta_radio_frequency_dispersion: float
    mcf: float
    # is that not
    tune_delay: int


@dataclass(frozen=True)
class MachineMetaData:
    model: str
    mode: str
    machine: str
    #: todo : should that not be machine meta data again ?
    submachine: str


@dataclass(frozen=True)
class MachineInfo:
    machine_type: MachineType
    standard_meta_data: MachineMetaData
    design_info: DesignInfo
    adjustment_info: AdjustmentInfo
