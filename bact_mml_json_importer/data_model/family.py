from dataclasses import dataclass
from typing import Sequence, Union

from .device.device import DeviceInfo
from .device.control_system_access import ControlSystemSignal
from .lattice.lattice_element_info import LatticeInstance
from .survey_info import SurveyInformation


@dataclass(frozen=True)
class DeviceCountInfo:
    """ """

    #: todo rename it to cell
    sector: int
    element_number: int


@dataclass(frozen=True)
class FamilyMember:
    _name: Union[str, None]
    type: str
    status: bool
    survey: SurveyInformation
    lattice: LatticeInstance
    pos: DeviceCountInfo
    dev_info: DeviceInfo

    @property
    def name(self):
        if self._name is not None:
            return self._name


@dataclass(frozen=True)
class Family:
    """

    Todo:
        what's the difference between family name and type
    """

    name: str
    elements: Sequence[FamilyMember]

    @property
    def type(self):
        return self.elements[0]

    def get(self, name: str) -> FamilyMember:
        def get_dict():
            """
            Todo:
                need to get result cached!
            """
            print(f"creating dict for family {self.name}")
            d = {elem.name: cnt for cnt, elem in enumerate(self.elements)}
            # are keys unique ?
            keys = list(d)
            assert len(keys) == len(list(set(keys)))
            return d

        return self.elements[get_dict()[name]]


@dataclass
class Families:
    elements: Sequence[Family]

    def get(self, name: str) -> Family:
        def get_dict():
            """
            Todo:
                need to get result cached!
            """
            print(f"creating dict for families")
            d = {fam.name: cnt for cnt, fam in enumerate(self.elements)}
            # are keys unique ?
            keys = list(d)
            assert len(keys) == len(list(set(keys)))
            return d

        return self.elements[get_dict()[name]]
