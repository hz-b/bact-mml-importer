from dataclasses import asdict
from typing import List, Any

from bact_mml_json_importer.app.families import handle_families
import argparse
import sys
import json
import jsons


from bact_mml_json_importer.app.inp import read_mml_in_json
from bact_mml_json_importer.app.machine import handle_machine_info
from bact_mml_json_importer.data_model.device.conversion_info import Magnet


def families(filename: str):
    repo = read_mml_in_json(filename=filename)
    return handle_families(repo)


def machine_description(filename: str):
    return handle_machine_info(read_mml_in_json(filename=filename))

def export_magnets_to_file(magnets: List[Magnet], filename: str):
    # convert dataclasses to plain dicts so json.dump can serialize
    serializable = [asdict(m) for m in magnets]
    with open(filename, "wt") as fp:
        json.dump(serializable, fp, indent=4)
def split_tango_descriptor(descriptor: str):
    parts = descriptor.split("/")
    if len(parts) < 4:
        raise ValueError(f"Invalid Tango descriptor: {descriptor}")
    return {
        "protocol": parts[0],
        "domain": parts[1],
        "family": parts[2],
        "member": "/".join(parts[3:]),
        "trl": "/".join(parts[0:3])
    }


def build_magnet_data(elem, *, type_name: str, subtype: str) -> Magnet:
    return Magnet(
        type=type_name,
        subtype=subtype,
        name=elem._name,
        forward_curve=elem.dev_info.monitor.info.forward,
        backward_curve=elem.dev_info.monitor.info.backward,
        pc=split_tango_descriptor(elem.dev_info.setpoint.comm.sig_name)["trl"]
    )


def export_for_dt4acc(families_data, filename: str):

    horizontal_steerers = [
        build_magnet_data(elem=elem, type_name="Steerer", subtype="horizontal")
        for elem in families_data.get("HCM").elements
    ]
    vertical_steerers = [
        build_magnet_data(elem=elem, type_name="Steerer", subtype="vertical")
        for elem in families_data.get("VCM").elements
    ]
    quadrupoles_o = [
        build_magnet_data(elem=elem, type_name="Quadrupole", subtype="O-dont-understand")
        for elem in families_data.get("SQFO").elements
    ]
    quadrupoles_i = [
        build_magnet_data(elem=elem, type_name="Quadrupole", subtype="I-dont-understand")
        for elem in families_data.get("SQFI").elements
    ]

    all_magnets = horizontal_steerers + vertical_steerers + quadrupoles_o + quadrupoles_i

    # bpm = families_data.get("BPMx")
    # tmp = jsons.dump(families_data)
    tmp = jsons.dump(all_magnets)
    with open(filename, "wt") as fp:
        json.dump(tmp, fp, indent=4)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--families-file", help="json data of the object returned by getao()")
    parser.add_argument("--description-file", help="json data of the object returned by getad()")
    parser.add_argument("--familes-file-export", help="export data from getao() to json file")
    out = parser.parse_args(sys.argv[1:])
    if out.description_file:
        des = machine_description(out.description_file)
        des

    if out.families_file:
        fam = families(out.families_file)
        export_for_dt4acc(
            fam,
            out.families_file.replace(".json", "_dt4acc.json")
        )
        fam

    if out.familes_file_export:
        tmp = jsons.dump(fam)
        with open(out.familes_file_export, "wt") as fp:
            json.dump(tmp,fp, indent=4)