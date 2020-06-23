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

def _collect_refs(obj):
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
            yield unpeel(obj['$ref'])
        else:
            for item in obj.values():
                for unpeeled in _collect_refs(item):
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
