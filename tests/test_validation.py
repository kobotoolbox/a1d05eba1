# from pprint import pprint
# import pytest
#
# from kobo.apps.formschema.content.content import Content
# from kobo.apps.formschema.kfrozendict import kfrozendict
#
#
# CONTENT_1 = {
#     'schema': '1',
#     'survey': [
#         {'type': 'select_one',
#             'select_from_list_name': 'xx',
#             'name': 'q1',
#             'label': [
#                 'label1',
#                 'label2',
#                 'label3'
#             ]
#         },
#     ],
#     'choices': [
#         {'list_name': 'xx', 'name': 'r1', 'label': ('r1a','r1b', 'r1c')},
#         {'list_name': 'xx', 'name': 'r2', 'label': ['r2a', 'r2b', 'r2c']},
#         {'list_name': 'xx', 'name': 'r3', 'label': ['r3a', 'r3b', 'r3c']},
#     ],
#     'translations': [
#         'a',
#         'b',
#         None,
#     ],
#     'translated': [
#         'label'
#     ],
#     'settings': {'id_string': 'example',},
# }
#
# CONTENT_2 = {
#     'schema': '2',
#     'survey': [
#         {'type': 'select_one',
#             'select_from': 'xx',
#             'name': 'q1',
#             'label': {
#                 'tx0': 'mylabel',
#             },
#         },
#     ],
#     'choices': {
#         'x1x': [
#             {
#                 'value': 'r1', 'label': {
#                     'tx0': 'r1'
#                 }
#             },
#             {
#                 'value': 'r2', 'label': {
#                     'tx0': 'r2'
#                 }
#             },
#             {
#                 'value': 'r3',
#                 'label': {
#                     'tx0': 'r3'
#                 }
#             },
#         ],
#     },
#     'translations': [
#         {
#             'name': 'eng',
#             '$anchor': 'tx0'
#         }
#     ],
#     'settings': {
#         'identifier': 'example',
#     },
# }
#
#
# def _content_no_validate(cc):
#     return Content(cc, perform_validation=False)
#
#
# def test_valid_s1_txs():
#     c1 = kfrozendict.freeze(CONTENT_1)
#     i1 = _content_no_validate(c1.copy(translations=['a', 'b', 'c']))
#     i1.validate()
#
#     i2 = _content_no_validate(c1.copy(translations=['a', 'b', None]))
#     i2.validate()
#
#
# def test_invalid_s1_txs():
#     c1 = kfrozendict.freeze(CONTENT_1)
#     iv1 = _content_no_validate(c1.copy(translations=['a', None, None]))
#     with pytest.raises(Exception):
#         iv1.validate()
#
#     iv2 = _content_no_validate(c1.copy(translations=['a', 'a', None]))
#     with pytest.raises(Exception):
#         iv2.validate()
#
# def test_invalid_s2_txs_duplicate():
#     c2 = kfrozendict.freeze(CONTENT_2)
#     x2 = _content_no_validate(c2.copy(translations=[
#         {'name': 't1', '$anchor': 'tx0'},
#         {'name': 't1', '$anchor': 'tx1'},
#     ]))
#     with pytest.raises(Exception):
#         x2.validate()
#
# def test_invalid_s2_txs_nulls():
#     c2 = kfrozendict.freeze(CONTENT_2)
#     x2 = _content_no_validate(c2.copy(translations=[
#         {'name': None, '$anchor': 'tx0'},
#         {'name': None, '$anchor': 'tx1'},
#     ]))
#     with pytest.raises(Exception):
#         x2.validate()
#
# def test_invalid_s2_txs_empty_str():
#     c2 = kfrozendict.freeze(CONTENT_2)
#     x2 = _content_no_validate(c2.copy(translations=[
#         {'name': '', '$anchor': 'tx0'},
#         {'name': 't1', '$anchor': 'tx1'},
#     ]))
#     with pytest.raises(Exception):
#         x2.validate()
#
# def test_invalid_s2_txs_empty_bad_codes():
#     invalid_codes = [
#         ('tx0', 'tx0'), # duplicates
#         ('tx0', None), # null code not allowed
#         ('tx0', ''), # empty string not allowed
#     ]
#     c2 = kfrozendict.freeze(CONTENT_2)
#     for (code1, code2) in invalid_codes:
#         with pytest.raises(Exception):
#             x2 = _content_no_validate(c2.copy(translations=[
#                 {'name': 't 0', '$anchor': code1},
#                 {'name': 't 1', '$anchor': code2},
#             ]))
#             x2.validate()
