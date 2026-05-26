import json
import jsons


def read_mml_in_json(filename):
    with open(filename, "rt") as fp:
        txt = json.load(fp)
    # Jsons would only make sense if we would state to which model to load to
    r = jsons.load(txt)
    return r
