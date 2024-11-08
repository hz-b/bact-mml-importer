import json
import jsons


def read_mml_in_json(filename):
    with open(filename, "rt") as fp:
        txt = json.load(fp)
    return jsons.load(txt)
