from typing import Mapping, Union

from ..data_model.machine import (
    MachineInfo,
    MachineMetaData,
    MachineType,
    DesignInfo,
    AdjustmentInfo,
)


def handle_machine_info(
    machine_json: Mapping[str, Union[str, float, int, Mapping]]
) -> MachineInfo:

    return MachineInfo(
        standard_meta_data=MachineMetaData(
            machine=machine_json["Machine"],
            submachine=machine_json["SubMachine"],
            model=machine_json["ATModel"],
            mode=machine_json["ModeName"],
        ),
        machine_type=MachineType(machine_json["MachineType"]),
        design_info=DesignInfo(
            #: Todo: convert to eV?
            energy=machine_json["Energy"],
            length=machine_json["Circumference"],
            injection_energy=machine_json["InjectionEnergy"],
            harmonic_number=machine_json["HarmonicNumber"],
        ),
        adjustment_info=AdjustmentInfo(
            delta_radio_frequency_dispersion=machine_json["DeltaRFDisp"],
            mcf=machine_json["MCF"],
            tune_delay=machine_json["TuneDelay"],
        ),
    )
