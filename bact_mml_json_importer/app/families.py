import itertools
import logging
from enum import Enum
from itertools import zip_longest
from typing import Mapping, Union, Sequence

from .util import make_single_entry_sequence_of_one
from ..data_model.device.control_system_access import (
    ControlSystemSignalType,
    ControlSystemSignal,
)
from ..data_model.device.conversion_info import ConversionInfo, CurvePoint, CurveBasedConversionInfo
from ..data_model.device.device import InfoCommChannel, UnitNames, DeviceInfo
from ..data_model.family import DeviceCountInfo, FamilyMember, Family, Families
from ..data_model.lattice.lattice_element_info import LatticeInstance
from ..data_model.survey_info import SurveyInformation

import numpy as np

logger = logging.getLogger("bact-mml-importer")


class ChannelType(Enum):
    readback = "readback"
    setpoint = "setpoint"


def zip_communication_conversion(info, comm_info):
    if len(info) == 1 and len(comm_info) > 1:
        for c in comm_info:
            yield info, c
    else:
        yield from zip_longest(info, comm_info)


def array_to_curve_based_conversion_info(arr):
    return CurveBasedConversionInfo(
        curve=[
            CurvePoint(indep=float(indep), dep=float(dep))
            for indep, dep in zip(arr[0], arr[1])
        ]
    )


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

    hw2physics = conversion_info.get("HW2PhysicsParams", None)
    L = L2 = None
    try:
        L = len(hw2physics)
    except TypeError:
        hw2physics = [hw2physics]

    physics2hw = conversion_info.get("Physics2HWParams", None)
    try:
        L2 = len(physics2hw)
    except TypeError:
        physics2hw = [physics2hw]

    assert L == L2, "Length of HW2PhysicsParams and Physics2HWParams differ"

    comm_dm = [
        ControlSystemSignal(
            sig_name=sig_name, type=sig_type, conversion_function_name=converter
        )
        for sig_name in channels
    ]



    if L == 1 and len(comm_dm) > 1:
        # how to improve the hack
        hw2physics = hw2physics[0]
        assert len(physics2hw) == 1
        physics2hw = physics2hw[0]
        if len(hw2physics)== len(comm_dm) * 2:
            assert len(hw2physics) % 2 == 0, f"Length of HW2PhysicsParams is not even"
            hw2p_a = np.array(hw2physics)
            p2hw_a = np.array(physics2hw)
            assert hw2p_a.shape[0] == p2hw_a.shape[0], "Sanity check failed"
            hw2p_a = hw2p_a.reshape([2, len(hw2physics) // 2, hw2p_a.shape[-1]])
            p2hw_a = p2hw_a.reshape([2, len(physics2hw) // 2, p2hw_a.shape[-1]])
            hw2p_a = hw2p_a.transpose([1, 0, 2])
            p2hw_a = p2hw_a.transpose([1, 0, 2])
            hw2physics = [array_to_curve_based_conversion_info(curve) for curve in hw2p_a]
            physics2hw = [array_to_curve_based_conversion_info(curve) for curve in p2hw_a]
        else:
            pass
           # assert   f"Length of HW2PhysicsParams {len(hw2physics)} does not match number of channels  {len(comm_dm)} * 2"


    conv_info_dm = [
        ConversionInfo(offset=offset, meta_gain=meta_gain, backward=hw2p, forward=p2hw)
        # Todo: change it to a zip that raises an exceptions if one of them is not as long as all oterhs
        for offset, meta_gain, hw2p, p2hw in zip_longest(
            offsets, meta_gain, hw2physics, physics2hw
        )
    ]

    info_comms = [
        InfoCommChannel(info=info, comm=comm)
        for info, comm in zip_communication_conversion(info=conv_info_dm, comm_info=comm_dm)
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
        hardware=readback.get("HWUnits", None), physics=readback.get("PhysicsUnits", None)
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


def handle_family_membersw(family_members: Mapping[str, Mapping], t_type: str):
    family_members = make_single_entry_sequence_of_one(family_members)
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
            for lattice_index in at_indices
        ]
    del lattice_info

    survey_pos = family_members.get("Position", None)
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
        common_names = [name.strip() for name in common_names]

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
            family_members["Status"],
            family_members["DeviceList"],
            family_members["ElementList"],
            wvf_idx,
            survey_device_info,
            lattice_elems_info,
            dev_cnt_info,
            dev_info,
        )
    ]
    return r

def handle_family_membersaa(family_members: Mapping[str, Mapping], t_type: str):
    family_members = make_single_entry_sequence_of_one(family_members)

    # -----------------------------
    # Number of magnets
    # -----------------------------
    device_list = family_members["DeviceList"]
    n_magnets = len(device_list)

    # -----------------------------
    # LATTICE HANDLING
    # -----------------------------
    lattice_info = family_members.get("AT", None)

    if lattice_info is None:
        lattice_elems_info = [None] * n_magnets
    else:
        lattice_type = lattice_info.get("ATType", None)
        at_param = lattice_info.get("ATParameterGroup", None)
        at_indices = None

        # ************* SQFI / SQFO CASE *************
        # Format: ATParameterGroup = [ [144 entries] ]
        if (
            isinstance(at_param, list)
            and len(at_param) == 1
            and isinstance(at_param[0], list)
            and len(at_param[0]) > n_magnets         # indicates multiplexed data
        ):
            inner = at_param[0]  # list of 144 (or more)
            seen = set()
            unique = []
            for entry in inner:
                idx = entry["ElemIndex"]
                if idx not in seen:
                    seen.add(idx)
                    unique.append(idx)

            # unique now contains the correct 48 AT indices
            at_indices = unique

        # ************* HCM / VCM NORMAL CASE *************
        else:
            at_indices = lattice_info.get("ATIndex", [None])

        # -----------------------------
        # normalize to exactly n_magnets
        # -----------------------------
        if len(at_indices) < n_magnets:
            at_indices = at_indices + [None] * (n_magnets - len(at_indices))
        elif len(at_indices) > n_magnets:
            at_indices = at_indices[:n_magnets]

        lattice_elems_info = [
            LatticeInstance(index=idx, type=lattice_type)
            for idx in at_indices
        ]

    # -----------------------------
    # SURVEY
    # -----------------------------
    survey_pos = family_members.get("Position", None)
    if survey_pos is None:
        survey_device_info = [None] * n_magnets
    else:
        survey_device_info = [
            SurveyInformation(longitudinal_position=s)
            for s in survey_pos
        ]

    # -----------------------------
    # DEVICE COUNT INFO
    # -----------------------------
    dev_cnt_info = [
        DeviceCountInfo(sector=sector, element_number=elem_num)
        for sector, elem_num in device_list
    ]

    # -----------------------------
    # DEVICE INFO
    # -----------------------------
    monitor = family_members.get("Monitor", None)
    if monitor is not None:
        dev_info = handle_device_info(
            family_members["Monitor"],
            family_members.get("Setpoint", None),
            n_magnets,
        )
    else:
        dev_info = [None] * n_magnets

    # -----------------------------
    # COMMON NAMES
    # -----------------------------
    wvf_idx = family_members.get("WaveRecordIndex", [None])

    common_names = family_members.get("CommonNames", None)
    if common_names is None:
        common_names = [None] * n_magnets
    else:
        if isinstance(common_names[0], list):
            common_names = list(itertools.chain(*common_names))
        common_names = [name.strip() for name in common_names]

        if len(common_names) < n_magnets:
            common_names = common_names + [None] * (n_magnets - len(common_names))
        else:
            common_names = common_names[:n_magnets]

    # -----------------------------
    # FINAL FAMILY MEMBERS
    # -----------------------------
    r = [
        FamilyMember(
            _name=name,
            type=t_type,
            status=status,
            survey=survey,
            dev_info=dev_i,
            lattice=lat_i,
            pos=pos,
        )
        for name, status, dev_list_entry, elem_entry,
            w_record, survey, lat_i, pos, dev_i
        in zip_longest(
            common_names,
            family_members["Status"],
            family_members["DeviceList"],
            family_members["ElementList"],
            wvf_idx,
            survey_device_info,
            lattice_elems_info,
            dev_cnt_info,
            dev_info,
        )
    ]

    return r

def handle_family_members(family_members: Mapping[str, Mapping], t_type: str):
    family_members = make_single_entry_sequence_of_one(family_members)
    fam_name = family_members["FamilyName"].lower()

    lattice_info = family_members.get("AT", None)

    if lattice_info is None:
        lattice_elems_info = [None]
    else:
        lattice_type = lattice_info.get("ATType", None)
        at_indices = lattice_info.get("ATIndex", [None])

        lattice_elems_info = [
            LatticeInstance(index=lattice_index, type=lattice_type)
            for lattice_index in at_indices
        ]

    survey_pos = family_members.get("Position", None)
    if survey_pos is None:
        survey_device_info = [None]
    else:
        survey_device_info = [
            SurveyInformation(longitudinal_position=s) for s in survey_pos
        ]

    dev_cnt_info = [
        DeviceCountInfo(sector=sector, element_number=elem_num)
        for sector, elem_num in family_members["DeviceList"]
    ]

    monitor = family_members.get("Monitor", None)
    if monitor is not None:
        dev_info = handle_device_info(
            family_members["Monitor"],
            family_members.get("Setpoint", None),
            len(dev_cnt_info),
        )
    else:
        dev_info = [None] * len(dev_cnt_info)

    wvf_idx = family_members.get("WaveRecordIndex", [None])

    common_names = family_members.get("CommonNames", None)
    if common_names is None:
        common_names = [None]
    else:
        if isinstance(common_names[0], list):
            common_names = list(itertools.chain(*common_names))
        common_names = [name.strip() for name in common_names]

    # ORIGINAL LIST (SQFI makes 144 here)
    r = [
        FamilyMember(
            _name=fam_name + str(lat_info.index) if lat_info else None,
            type=t_type,
            status=status,
            survey=survey,
            dev_info=dev_info,
            lattice=lat_info,
            pos=pos,
        )
        for name, status, device_index, element_index, wave_record_index,
            survey, lat_info, pos, dev_info in zip_longest(
                common_names,
                family_members["Status"],
                family_members["DeviceList"],
                family_members["ElementList"],
                wvf_idx,
                survey_device_info,
                lattice_elems_info,
                dev_cnt_info,
                dev_info,
            )
    ]

    # ----------------------------------------------------------------------
    # SQFI FIX (144 → 48) — rebuild FamilyMember with correct names + fields
    # ----------------------------------------------------------------------
    if fam_name == "sqfi":
        r = r[:48]
        base = r[0]

        new_list = []
        for i in range(48):
            src = r[i]
            new_list.append(
                FamilyMember(
                    _name=fam_name + str(src.lattice.index),
                    type=base.type,
                    status=base.status,
                    survey=base.survey,
                    dev_info=base.dev_info,
                    lattice=LatticeInstance(
                        index=src.lattice.index,
                        type=base.lattice.type
                    ),
                    pos=src.pos,
                )
            )

        r = new_list

    return r

def handle_families(families_json: Mapping[str, Union[str, Mapping]]) -> Families:
    def convert(families_info):
        t_type = families_info.get("FamilyType")
        name = families_info.get("FamilyName")
        if name in ["CAVITY", "LANDAU"]:
            return None
        try:
            elems = handle_family_members(families_info, t_type)
            elems = [elem for elem in elems if elem is not None]
            r =  Family(
                name=families_info.get("FamilyName"),
                elements=elems
            )
        except Exception as exc:

            logger.error(f"Treating family members failed for {t_type} {name}")
            raise exc
        return r

    fams = [convert(families_info) for _, families_info in families_json.items()]
    return Families(
        elements=[f for f in fams if f is not None]
    )
