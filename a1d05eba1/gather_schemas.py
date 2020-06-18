# this is a fugly file that pulls together the yml files and turns them into
# different jsonschemas

import os

from .utils.yparse import yparse, yload_file, invert, yload_definition, dir_path


BASE_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'survey':  { '$ref': '#/$defs/survey' },
        'translations': {'$ref': '#/$defs/translations' },
        'choices': { '$ref': '#/$defs/choices' },
        'settings': {'$ref': '#/$defs/settings'},
    },
}

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


INDIVIDUAL_SCHEMA_NAMES = [ref for ref in _collect_refs(BASE_SCHEMA)]

YLOADED_FILES = {}
_DEFINITIONS = {}


remap = {}

import os

def path_for_def(defid):
    return os.path.join(dir_path, '..', 'yml', 'defs', defid) + '.yml'

def _load_schema_section(fullpath):
    fullpath = remap.get(fullpath, fullpath)
    if fullpath in YLOADED_FILES:
        raise Exception('double loaded?')

    (defdir, defid) = fullpath.split('/')
    savepath = fullpath
    defid_path = path_for_def(defid)
    if os.path.exists(defid_path):
        getpath = fullpath
    else:
        defid = '_' + defid
        defid_path = path_for_def(defid)
        getpath = '{}/{}'.format(defdir, defid)

    section = yload_file(getpath)

    YLOADED_FILES[savepath] = section
    loaded = YLOADED_FILES[savepath]

    path = fullpath.split('/')[-1]
    if 'definitions' in loaded or '$defs' in loaded:
        raise Exceptions('"$defs" must be moved into individual files of '
                         'yml/defs/*.yml')

    other_paths_to_load = [ref for ref in _collect_refs(loaded)]
    _DEFINITIONS[path] = loaded

    for other_path in other_paths_to_load:
        if other_path not in _DEFINITIONS:
            _load_schema_section('defs/{}'.format(other_path))

for schema_section_name in INDIVIDUAL_SCHEMA_NAMES:
    _load_schema_section('defs/{}'.format(schema_section_name))

MAIN = dict({
    '$defs': _DEFINITIONS,
}, **BASE_SCHEMA)

SCHEMAS = {}
for schema_name in INDIVIDUAL_SCHEMA_NAMES:
    nooschema = {}
    noodefs = {}
    base = _DEFINITIONS[schema_name]
    for defname in _collect_refs(base):
        noodefs[defname] = _DEFINITIONS[defname]
    nooschema['$defs'] = noodefs
    SCHEMAS[schema_name] = nooschema
SCHEMAS['MAIN'] = MAIN

import json
SCHEMAS_LOOSE = json.loads(json.dumps(SCHEMAS).replace('"additionalProperties": false', '"additionalProperties": true'))
