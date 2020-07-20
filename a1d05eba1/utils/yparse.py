import yaml
from jsonschema import Draft6Validator

import os
dir_path = os.path.dirname(os.path.realpath(__file__))


def yload_file(filename, invert=False):
    parts = filename.split('/')
    (dir, filename) = [parts[:-1], parts[-1]]
    _dir_path = os.path.abspath(os.path.join(dir_path, '..', 'yml', *dir))
    filepath = os.path.join(_dir_path, '{}.yml'.format(filename))
    if not os.path.exists(filepath):
        raise ValueError('yml file does not exist: {}'.format(filepath))
    with open(filepath, 'r') as ff:
        obj = yaml.full_load(ff.read())
    if invert:
        obj = _invert(obj)
    return obj

def _invert(dct):
    out = {}
    for (key, vals) in dct.items():
        for val in vals:
            out[val] = key
    return out
