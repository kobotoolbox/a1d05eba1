import os
import yaml

from .exceptions import SchemaRefError

from .YAML_CONSTANTS import YAML_CONSTANTS

BASE_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'schema': { 'type': 'string' },
        'survey':  { '$ref': '#/$defs/survey' },
        'translations': {'$ref': '#/$defs/translations' },
        'choices': { '$ref': '#/$defs/choices' },
        'settings': {'$ref': '#/$defs/settings'},
    },
}

project_path = os.path.dirname(os.path.realpath(__file__))
YML_DIR = os.path.join(project_path, 'yml')
defpath = lambda defid: os.path.join(YML_DIR, 'defs', defid + '.yml')

def _load_path(fpath):
    with open(fpath, 'r') as ff:
        yaml_in = ff.read()
    for (val, rep_with) in YAML_CONSTANTS:
        if val in yaml_in:
            yaml_in = yaml_in.replace(val, rep_with)
    return yaml.full_load(yaml_in)

BASE_SCHEMA = _load_path(os.path.join(YML_DIR, 'schema.yml'))

def _collect_refs(obj, parent_key=''):
    '''
    iterate through a jsonschema object or list and yield
        'xyz'
    for any:
        {'$ref':'#/$defs/xyz'}
    that are found
    '''
    unpeel = lambda ss: ss.replace('#/$defs/', '')

    if isinstance(obj, dict):
        if '$ref' in obj:
            if parent_key != 'properties':
                # $ref is a property, not a reference to a def
                yield unpeel(obj['$ref'])
        else:
            for (key, item) in obj.items():
                for unpeeled in _collect_refs(item, parent_key=key):
                    yield unpeeled
    elif isinstance(obj, list):
        for item in obj:
            for unpeeled in _collect_refs(item):
                yield unpeeled


def build_schema(base_schema=None):
    if base_schema is None:
        base_schema = BASE_SCHEMA
    loaded = {}
    def load_schema_partials(content):
        for part in _collect_refs(content):
            if part in loaded:
                continue
            _parts = [part, '_{}'.format(part)]
            _files = [defpath(fp) for fp in _parts]
            _exists = [os.path.exists(pf) for pf in _files]
            ref_error = False
            if _exists[0] and _exists[1]:
                ref_error = 'Conflicting ref files for "#/$defs/{}": {}, {}'
            elif not (_exists[0] or _exists[1]):
                ref_error = 'No ref file for "#/$defs/{}": {} or {}'
            if ref_error:
                raise SchemaRefError(ref_error.format(part, *_parts))
            fpath = _files[0] if _exists[0] else _files[1]
            loaded[part] = _load_path(fpath)
            load_schema_partials(loaded[part])
    load_schema_partials(base_schema)
    return {'$defs': loaded,
            **base_schema}

MAIN_SCHEMA = build_schema()
JSONSCHEMA = MAIN_SCHEMA

from jsonschema import Draft7Validator
Draft7Validator.check_schema(MAIN_SCHEMA)

_defs = {}
for (key, val) in JSONSCHEMA['$defs'].items():
    Draft7Validator.check_schema(val)
    _defs[key] = val

_individual_defs = {}
def schema_for_def(defname):
    if defname not in _individual_defs:
        _subdefs = {}
        def append_ref_and_subrefs(xdef, key):
            if key:
                _subdefs[key] = xdef
            for ref in _collect_refs(xdef):
                if ref not in _subdefs:
                    append_ref_and_subrefs(_defs[ref], ref)
        _def = _defs[defname]
        append_ref_and_subrefs(_def, key=False)
        _individual_defs[defname] = {**_def, '$defs': _subdefs}
    return _individual_defs[defname]
