import functools
from dataclasses import dataclass
from typing import Sequence, Union, Dict

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
    member_of : Sequence[str]

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
        return self._family_member_by_name[name]

    @functools.cached_property
    def _family_member_by_name(self) -> Dict[str, FamilyMember]:
        d = {elem.name: elem for elem in self.elements if elem.name is not None}
        # are keys unique ?
        keys = list(d)
        assert len(keys) == len(list(set(keys)))
        return d


@dataclass
class Families:
    elements: Sequence[Family]

    def get(self, name: str) -> Family:
        return self._family_by_name[name]

    @functools.cached_property
    def _family_by_name(self) -> Dict[str, Family]:
        d = {elem.name: elem for elem in self.elements if elem.name is not None}
        # are keys unique ?
        keys = list(d)
        assert len(keys) == len(list(set(keys)))
        return d
