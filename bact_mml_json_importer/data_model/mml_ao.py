import logging
from typing import Mapping, Union, Sequence, Tuple, Dict, TypeVar

from pydantic import BaseModel, ValidationError

from bact_mml_json_importer.data_model.utils import normalize_nested_sequence, ensure_sequence

logger = logging.getLogger("bact-mml-importer")


class ATElementsInfo(BaseModel):
    """To which element does the device connect to

    Should be always a sequence of integers
    """
    ATType: str
    ATIndex: int | Sequence[int] | Sequence[Sequence[int]]

    def get_element_indices(self) -> list[list[int]]:
        return normalize_nested_sequence(self.ATIndex, int)


# @dataclass
class ConversionFunctionHandle(BaseModel):
    """function name and file name that does the conversion

    Todo:
        Understand the type simple
    """
    file: str
    function: str
    type: str


class ConversionFunction(BaseModel):
    # delegate to match ao object
    function_handle: ConversionFunctionHandle


class _MonitorBase(BaseModel):
    ChannelNames: Sequence[str] | str
    MemberOf: list[str] | None = None
    DataType: str
    Units: str
    # required for ALS ao data: HWUnits shown as empty string for RF data
    HWUnits: str | list[str]
    # required for ALS ao data : HWUnits shown as empty string for RF data
    PhysicsUnits: str | list[str]
    Mode: str | None  = None
    MetaGain:  Sequence[float] | None  = None
    PhysicalUnits: str | None  = None
    HW2PhysicsParams: Sequence[float] | float | None = None
    Physics2HWParams: Sequence[float] | float | None = None
    HW2PhysicsFcn: ConversionFunction | None = None
    Physics2HWFcn: ConversionFunction | None = None


class MonitorDataModel(_MonitorBase):
    pass
    # model_config = ConfigDict(extra='allow')


# @dataclass
class SetpointDataModel(_MonitorBase):
    Range: Sequence[Tuple[float, float]] | Tuple[float, float]


# @dataclass
class FamilyInfoCollection(BaseModel):
    """Collected info entries following Matlab Middle Layer ao object

    Todo:
        make the model more stringent: e.g. MemberOf shall be always a
        sequence. Need to see what pydantic provides for that

        Need to address channels beyond Monitor and Setpoint
    """
    MemberOf: Sequence[str] | str
    CommonNames: Sequence[str] | str | None = None
    DeviceList : Sequence[Tuple[int,int]] | Tuple[int,int]
    ElementList : Sequence[int] | int
    Status: Union[int, Sequence[int]]
    Position : Sequence[float] | float | None = None
    Monitor: MonitorDataModel | None = None
    Offset: Sequence[float] | None = None
    Setpoint: SetpointDataModel | None = None
    AT: ATElementsInfo | None = None

    # model_config = ConfigDict(extra='allow')

    def get_device_list(self) -> list[tuple[int, int]]:
        if isinstance(self.DeviceList, tuple):
            return [self.DeviceList]
        return self.DeviceList

    def member_of(self) -> Sequence[str]:
        return ensure_sequence(self.MemberOf)

    def get_device_index(self, sector:int, child:int) -> int:
        return self.get_device_list().index((sector, child))


def load(data: Mapping[str, Union[str, Mapping]]) -> Dict[str, FamilyInfoCollection]:
    d = dict()
    for family_name, item in data.items():
        # if family_name in ["TUNE", "DCCT"]:
        #     continue
        try:
            model = FamilyInfoCollection(**item)
        except ValidationError as ve:
            logger.error(f"Conversion failed for family {family_name}: {ve}" )
            continue
        d[family_name] = model
    return d
