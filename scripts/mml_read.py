from typing import Sequence, Union

from bact_mml_json_importer.app.families import handle_families
import argparse
import sys

from bact_mml_json_importer.app.inp import read_mml_in_json
from bact_mml_json_importer.app.machine import handle_machine_info
from bact_mml_json_importer.data_model.mml_ao import load
from bact_mml_json_importer.util import clear_hw2physics


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
