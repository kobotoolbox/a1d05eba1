from .build_schema import MAIN_JSONSCHEMA
from .utils.yparse import yload_file as yload

from copy import deepcopy



def override_prop(schema, key, val):
    schema['properties'][key] = val
def _remove_root_prop(schema, key):
    del schema['properties'][key]
def _survey_row_type_alternative(schema, val):
    srt = schema['$defs']['surveyRowType']
    if 'oneOf' not in srt:
        schema['$defs']['surveyRowType'] = {
            'oneOf': [srt]
        }
    one_of = schema['$defs']['surveyRowType']['oneOf']
    one_of.append(val)
def _add_row_types(schema, additional_row_types):
    SRT = schema['$defs']['surveyRowType']
    SRT['enum'] = SRT['enum'] + additional_row_types
def _unlink_grouping_from_survey_items(schema):
    schema['$defs']['survey']['items'] = {'$ref': '#/$defs/surveyRow'}
def override_def(schema, key, val):
    schema['$defs'][key] = val
def update_def_props(schema, key, props):
    schema['$defs'][key]['properties'].update(props)


xlsform = deepcopy(MAIN_JSONSCHEMA)
koboxlsform = deepcopy(MAIN_JSONSCHEMA)
fp0 = deepcopy(MAIN_JSONSCHEMA)
fp1 = deepcopy(MAIN_JSONSCHEMA)
fp2 = deepcopy(MAIN_JSONSCHEMA)
formpacks = [fp0, fp1, fp2]


_unlink_grouping_from_survey_items(koboxlsform)
_unlink_grouping_from_survey_items(xlsform)
for fp in formpacks:
    _unlink_grouping_from_survey_items(fp)


def _add_surveyRow_col_string(schema, prop):
    update_def_props(schema, 'surveyRow', {prop: {'type': 'string'}})

def _allow_other_surveyrow_props(schema):
    schema['$defs']['surveyRow']['additionalProperties'] = True


override_prop(koboxlsform, 'translated', {
    'type': 'array',
    'items': {
        'type': 'string',
    }
})

override_prop(koboxlsform, 'translations', {
    'type': 'array',
    'items': {
        'anyOf': [
            {'type': 'string'},
            {'type': 'null'},
        ]
    }
})

for (index, fp) in enumerate(formpacks):
    txschema = {
        'type': 'array',
        'items': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'},
            ]
        },
    }

    if index == 0:
        override_def(fp, 'translatable', {'type': 'string'})
        txschema['maxItems'] = 0
    else:
        txschema['minItems'] = txschema['maxItems'] = index
        override_def(fp, 'translatable', {'type': 'array',
            'items': {'type': 'string'},
            'maxItems': index,
        })

    override_prop(fp, 'translations', txschema)



override_def(koboxlsform, 'translatable', {
    'type': 'array',
    'items': {'type': 'string',},
})
override_def(xlsform, 'translatable', {'type': 'string'})


for (index, fp) in enumerate(formpacks):
    if index == 0:
        override_def(fp, 'translatable', {'type': 'string'})
    else:
        override_def(fp, 'translatable', {'type': 'array',
            'items': {'type': 'string'},
            'maxItems': index,
        })


override_def(xlsform, 'choices', {'type': 'array',})

for fp in formpacks:
    override_def(fp, 'choices', {'type': 'array',})


update_def_props(xlsform, 'settings', {
    'formid': {'type': 'string'},
})

_add_surveyRow_col_string(koboxlsform, '$kuid')
_add_surveyRow_col_string(xlsform, 'media::audio')

# not sure if kuid is necessary here
_add_surveyRow_col_string(xlsform, '$kuid')

override_prop(xlsform, 'settings', {
    'type':'array',
    'minItems': 1,
    'items': {'$ref': '#/$defs/settings'}
})

_remove_root_prop(xlsform, 'metas')
_remove_root_prop(koboxlsform, 'metas')

renamed_metas = list(iter(yload('renames/from1/metas', invert=True).keys()))
meta_types = list(iter(MAIN_JSONSCHEMA['$defs']['metas']['properties'].keys()))
renamed_types = list(iter(yload('renames/from1/xlsformTypes', invert=True).keys()))

_add_row_types(xlsform, renamed_metas)
_add_row_types(xlsform, meta_types)
_add_row_types(xlsform, renamed_types)

for fp in formpacks:
    _add_row_types(fp, renamed_types)

for fp in formpacks:
    _allow_other_surveyrow_props(fp)

for fp in formpacks:
    override_def(fp, 'notFalseyBooleanString', {})

FORMPACK_SCHEMA = {
    'type': 'object',
    'oneOf': formpacks,
}
XLSFORM_SCHEMA = xlsform
KOBOXLSFORM_SCHEMA = koboxlsform
