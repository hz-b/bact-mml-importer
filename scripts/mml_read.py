from typing import Sequence, Union

from bact_mml_json_importer.app.families import handle_families
import argparse
import sys

from bact_mml_json_importer.app.inp import read_mml_in_json
from bact_mml_json_importer.app.load_with_jsons import load
from bact_mml_json_importer.app.machine import handle_machine_info

def to_single_float_removing_zeros(values: Sequence[Union[float,int]]) -> float:
    r, =  [val for val in values if val != 0]
    return r

def clear_hw2physics(bpm_data, copy:bool=True):
    if copy:
        bpm_data = bpm_data.copy()
    t_vals = bpm_data["Monitor"]["HW2PhysicsParams"]
    vals = [
        to_single_float_removing_zeros(val) for val in t_vals
    ]
    bpm_data["Monitor"]["HW2PhysicsParams"] = vals
    return bpm_data



def families(filename: str):
    data = read_mml_in_json(filename=filename)
    clear_hw2physics(data["BPMx"], copy=False)
    clear_hw2physics(data["BPMy"], copy=False)
    r = load(data)
    # Todo: remove that if feasable
    # data = data["ao"]
    return handle_families(data)


def machine_description(filename: str):
    r = handle_machine_info(read_mml_in_json(filename=filename))
    return r


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--families-file", help="json data of the object returned by getao()")
    parser.add_argument("--description-file", help="json data of the object returned by getad()")
    out = parser.parse_args(sys.argv[1:])
    if out.description_file:
        des = machine_description(out.description_file)
        des

    if out.families_file:
        fam = families(out.families_file)
        fam
