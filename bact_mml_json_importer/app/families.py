import itertools
import logging
from enum import Enum
from itertools import zip_longest
from typing import Mapping, Union, Sequence

import numpy as np

from .util import make_single_entry_sequence_of_one
from ..data_model.device.control_system_access import (
    ControlSystemSignalType,
    ControlSystemSignal,
)
from ..data_model.device.conversion_info import ConversionInfo
from ..data_model.device.device import InfoCommChannel, UnitNames, DeviceInfo
from ..data_model.family import DeviceCountInfo, FamilyMember, Family, Families
from ..data_model.lattice.lattice_element_info import LatticeInstance
from ..data_model.survey_info import SurveyInformation

logger = logging.getLogger("bact-mml-exporter")

class ChannelType(Enum):
    readback = "readback"
    setpoint = "setpoint"


def handle_conversion_info(
    conversion_info: Mapping[str, Union[None, str, Sequence[Union[str, float]]]],
    channel_type: ChannelType,
    n_elements: int,
):

    channels = conversion_info.get("ChannelNames")
    if not channels:
        channels = [None] * n_elements

    channel_type = ChannelType(channel_type)
    if channel_type == ChannelType.readback:
        converter = conversion_info.get("SpecialFunctionGet")
        sig_type = ControlSystemSignalType.read_only
    elif channel_type == ChannelType.setpoint:
        converter = conversion_info.get("SpecialFunctionSet")
        sig_type = ControlSystemSignalType.read_write
    else:
        raise AssertionError("Sanity check: should not end up here")

    # prepared for one signal here .. not 2
    offsets = conversion_info.get("Offset")
    if offsets is None:
        offsets = [None] * n_elements
    meta_gain = conversion_info.get("MetaGain")
    if meta_gain is None:
        meta_gain = [None] * n_elements

    # have to be vectors
    len(channels)
    len(offsets)
    len(meta_gain)

    try:
        hw2physics = conversion_info["HW2PhysicsParams"]
        hw2physics = np.atleast_1d(hw2physics)
    except KeyError as ke:
        logger.error("No HW2PhysicsParams in conversion_info for ")
        hw2physics = [None]
    # todo: use np.atleast_1d

    # todo: use np.atleast_1d
    try:
        physics2hw = conversion_info["Physics2HWParams"]
        physics2hw = np.atleast_1d(physics2hw)
    except KeyError:
        physics2hw = [None]

    conv_info_dm = [
        ConversionInfo(offset=offset, meta_gain=meta_gain, backward=hw2p, forward=p2hw)
        for offset, meta_gain, hw2p, p2hw in zip_longest(
            offsets, meta_gain, hw2physics, physics2hw
        )
    ]

    comm_dm = [
        ControlSystemSignal(
            sig_name=sig_name, type=sig_type, conversion_function_name=converter
        )
        for sig_name in channels
    ]
    info_comms = [
        InfoCommChannel(info=info, comm=comm)
        for info, comm in zip(conv_info_dm, comm_dm)
    ]
    return info_comms


def handle_device_info(
    readback: Mapping[str, Union[str, Sequence[Union[str, float]]]],
    setpoint: Mapping[str, Union[str, Sequence[Union[str, float]]]],
    n_elements: int,
):

    conv_info_rdbk = handle_conversion_info(
        readback, ChannelType.readback, n_elements=n_elements
    )
    if setpoint:
        conv_info_setp = handle_conversion_info(
            setpoint, ChannelType.setpoint, n_elements=n_elements
        )
        limits = setpoint.get("Range", [None] * len(conv_info_rdbk))
    else:
        conv_info_setp = [None] * len(conv_info_rdbk)
        limits = [None] * len(conv_info_rdbk)
    unit_names = UnitNames(
        hardware=readback["HWUnits"], physics=readback["PhysicsUnits"]
    )
    getter = readback.get("SpecialFunctionGet")

    r = [
        DeviceInfo(
            unit_names=unit_names,
            limits=lim,
            setpoint=setp,
            monitor=rdbk,
        )
        for setp, rdbk, lim in zip(conv_info_setp, conv_info_rdbk, limits)
    ]
    return r


def handle_family_members(family_members: Mapping[str, Mapping], t_type: str):
    family_members = make_single_entry_sequence_of_one(family_members)
    if not family_members:
        return None
    lattice_info = family_members.get("AT", None)
    if lattice_info is None:
        lattice_elems_info = [None]
    else:
        lattice_type = lattice_info.get("ATType", None)
        if lattice_type is None:
            lattice_type
        at_indices = lattice_info.get("ATIndex", [None])

        lattice_elems_info = [
            LatticeInstance(index=lattice_index, type=lattice_type)
            for lattice_index in zip(at_indices)
        ]
    del lattice_info

    survey_pos = np.atleast_1d(family_members.get("Position", None))
    if survey_pos is None:
        survey_device_info = [None]
    else:
        survey_device_info = [
            SurveyInformation(longitudinal_position=s) for s in survey_pos
        ]
    del survey_pos

    dev_cnt_info = [
        DeviceCountInfo(sector=sector, element_number=elem_num)
        for sector, elem_num in family_members["DeviceList"]
    ]

    # For MAX-IV data ...
    monitor = family_members.get("Monitor", None)
    if monitor is not None:
        dev_info = handle_device_info(
            family_members["Monitor"],
            family_members.get("Setpoint", None),
            len(dev_cnt_info),
        )
    else:
        # not handliny yet dedicated channels
        dev_info = [None] * len(dev_cnt_info)

    wvf_idx = family_members.get("WaveRecordIndex", [None])
    if wvf_idx is None:
        pass
    common_names = family_members.get("CommonNames", None)
    if common_names is None:
        # Todo: can we let that pass on ?
        common_names = [None]
    else:
        if isinstance(common_names[0], list):
            # needed for MAX IV: R3-3/MAG/CROYY-01, R3-A101911/RF/MO-01
            common_names = list(itertools.chain(*common_names))
        def clear_name(name):
            if name is None:
                return None
            return name.strip()
        common_names = [clear_name(name) for name in common_names]

    r = [
        FamilyMember(
            _name=name,
            type=t_type,
            status=status,
            survey=survey,
            dev_info=dev_info,
            lattice=lat_info,
            pos=pos,
        )
        for name, status, device_index, element_index, wave_record_index, survey, lat_info, pos, dev_info in zip_longest(
            common_names,
            np.atleast_1d(family_members["Status"]),
            np.atleast_2d(family_members["DeviceList"]),
            np.atleast_1d(family_members["ElementList"]),
            wvf_idx,
            survey_device_info,
            lattice_elems_info,
            dev_cnt_info,
            dev_info,
        )
    ]
    return r


def handle_families(families_json: Mapping[str, Union[str, Mapping]]) -> Families:
    def convert(families_info):
        t_type = families_info.get("FamilyType")
        return Family(
            name=families_info.get("FamilyName"),
            elements=handle_family_members(families_info, t_type),
        )

    return Families(
        elements=[convert(families_info) for _, families_info in families_json.items()]
    )
