from a1d05eba1.content import Content


from a1d05eba1.utils.kfrozendict import kfrozendict

from jsonschema import validate

from pprint import pprint

from a1d05eba1.build_schema import MAIN_JSONSCHEMA
from a1d05eba1.build_schema import schema_for_def

from jsonschema import Draft7Validator

from a1d05eba1.schemas import KOBOXLSFORM_SCHEMA
from a1d05eba1.schemas import XLSFORM_SCHEMA
from a1d05eba1.schemas import FORMPACK_SCHEMA

SCHEMA_DEFS = MAIN_JSONSCHEMA['$defs']

def test_schemas_for_individual_defs():
    for subschema_name in [
        'choice',
        'surveyRow',
        'translatable',
    ]:
        ssk = schema_for_def(subschema_name)
        assert '$defs' in ssk
        Draft7Validator.check_schema(ssk)

def test_row_schema():
    schema = schema_for_def('surveyRow')
    assert set(schema['$defs'].keys()) == set([
        'translatable',
        'xpath',
        'choiceFilter',
        'booleanOrXpath',
        'nameString',
        'notFalseyBooleanString',
        'surveyRowType',
        'translatableMedia',
        'type--boolean',
        'type--filecode',
        'type--null',
        'type--string',
        'type--url',
    ])

def test_settings_schema():
    schema = schema_for_def('settings')
    assert set(schema['$defs'].keys()) == set([
        'type--url',
    ])

def test_translation_schema():
    schema = schema_for_def('translations')
    assert set(schema['$defs'].keys()) == set(['translationsItem'])


def test_koboxlsform_schema():
    validate({
        'translations': ['english', 'french', None],
        'survey': [
            {'type': 'text',
             'label': ['aaa'],
             },
        ]
    }, KOBOXLSFORM_SCHEMA)

def test_basics_of_schemas():
    assert 'metas' not in KOBOXLSFORM_SCHEMA['properties']
    assert 'metas' not in XLSFORM_SCHEMA['properties']
    assert 'metas' not in XLSFORM_SCHEMA['properties']
