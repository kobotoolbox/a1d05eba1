import yaml
from jsonschema import Draft6Validator

import os
dir_path = os.path.dirname(os.path.realpath(__file__))


def yparse(ycontent):
    schema = yaml.full_load(ycontent)
    Draft6Validator.check_schema(schema)
    return schema


def yload_file(filename, invert=False, dir=None):
    if dir is not None:
        raise Exception('no dir')
    parts = filename.split('/')
    (dir, filename) = [parts[:-1], parts[-1]]

    xx = False
    if filename is 'rowType':
        xx = True
    if dir is None:
        dir = tuple()
    _dir_path = os.path.abspath(os.path.join(dir_path, '..', 'yml', *dir))
    filepath = os.path.join(_dir_path, '{}.yml'.format(filename))
    if not os.path.exists(filepath):
        raise ValueError('yml file does not exist: {}'.format(filepath))
    with open(filepath, 'r') as ff:
        qq = ff.read()
        for (rep_from, rep_to) in [
            ('TXCODE_REGEX_SEE_GATHER_SCHEMAS_PY', '^[a-zA-Z0-9_]{2,6}$'),
            ('CHOICELIST_NAME_REGEX_SEE_GATHER_SCHEMAS_PY', '.*'),
        ]:
            qq = qq.replace(rep_from, rep_to)

        if 'definitions' in qq:
            raise Exception('defs in ' + filename)
        obj = yaml.full_load(qq)
    if invert:
        obj = _invert(obj)
    return obj

def yload_definition(definition_name):
    defname = definition_name.replace('#/definitions/', '')
    return (
        defname,
        yload_file(defname, dir=('definitions',))
    )

def invert(dct):
    out = {}
    for (key, vals) in dct.items():
        for val in vals:
            out[val] = key
    return out

def _invert(dd):
    return invert(dd)
