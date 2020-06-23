from a1d05eba1.content import Content


from a1d05eba1.utils.kfrozendict import kfrozendict

from jsonschema import validate

from pprint import pprint

from a1d05eba1.build_schema import MAIN_SCHEMA

SCHEMA_DEFS = MAIN_SCHEMA['$defs']

# def test_choice_schema():
#     schema = SCHEMA_DEFS['choice']
#     assert set(schema['$defs'].keys()) == set([
#         'translatable'
#     ])
#
# def test_row_schema():
#     schema = SCHEMAS['row']
#     assert set(schema['$defs'].keys()) == set([
#         'translatable',
#         'xpath',
#         'booleanOrXpath',
#         'alphanumericValue',
#         'rowType',
#         'translatableMedia',
#     ])
#
# def test_settings_schema():
#     schema = SCHEMAS['settings']
#     assert set(schema['$defs'].keys()) == set()
#
# def test_translation_schema():
#     schema = SCHEMAS['translation']
#     assert set(schema['$defs'].keys()) == set()


# import pytest
#
# def test_voloo():
#     # with pytest.raises(Exception):
#     validate({
#         'Z9_Z0': 'def',
#         'X3_B0': 'abcd',
#     }, {
#         'type': 'object',
#         'additionalProperties': False,
#         'patternProperties': {
#             '\\w\\d_\\w\\d': {'$ref': '#/definitions/straang'}
#         },
#         '$defs': {
#             'straang': {
#                 'type': 'string'
#             }
#         }
#     })


# import locale
# aliases = [kv for kv in locale.locale_alias]
#
# import re
#
# def test_re():
#     restr = r'^[a-z].{0,20}$'
#     for kv in locale.locale_alias:
#         if not re.match(restr, kv):
#             raise Exception('zz '+kv)

# from pprint import pprint
# pprint(aliases)
