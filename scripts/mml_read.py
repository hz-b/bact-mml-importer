from bact_mml_json_importer.app.families import handle_families
import argparse
import sys

from bact_mml_json_importer.app.inp import read_mml_in_json
from bact_mml_json_importer.app.machine import handle_machine_info


def families(filename: str):
    return handle_families(read_mml_in_json(filename=filename))


def machine_description(filename: str):
    return handle_machine_info(read_mml_in_json(filename=filename))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--families-file", help="json data of the object returned by getao()")
    parser.add_argument("--description-file", help="json data of the object returned by getad()")
    out = parser.parse_args(sys.argv[1:])
    if out.families_file:
        fam = families(out.families_file)
        fam
    if out.description_file:
        machine_description(out.description_file)
