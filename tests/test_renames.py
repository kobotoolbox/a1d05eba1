from a1d05eba1.content import Content
from a1d05eba1.components.row import Row
from a1d05eba1.components.choices import Choice

from a1d05eba1.utils.kfrozendict import kfrozendict

# from kobo.apps.formschema.content.content import Content, Choice
# from kobo.apps.formschema.content.row import Row
#
# # from frozendict import frozendict
# from kobo.apps.formschema.kfrozendict import kfrozendict

from pprint import pprint

BAREBONES_1 = kfrozendict({
    'schema': '1',
    'translated': [],
    'survey': [],
    'settings': {},
    'translations': [None],
})


def test_renames_column_on_import():
    cc1 = BAREBONES_1.copy(translated=(
        'media::image',
    ))
    cc2 = Content(cc1)
    row = Row(content=cc2, row={
        'type': 'text',
        '$anchor': 'uniqueanchor',
        'media::image': ['abc']
    })

    _keys = [val.key for val in row]
    assert 'image' in _keys
    assert 'media::image' not in _keys


def test_reverts_certain_names_on_export():
    cc1 = BAREBONES_1.copy(translated=(
        'media::image',
    ))
    cc2 = Content(cc1)
    row = Row(content=cc2, row={
        'type': 'text',
        '$anchor': 'x',
        'media::image': ['abc']
    })

    schema = '1'
    assert 'image' not in row.flat_export(schema=schema)
    assert 'media::image' in row.flat_export(schema=schema)

    schema = '2'
    assert 'image' in row.flat_export(schema=schema)
    assert 'media::image' not in row.flat_export(schema=schema)


def test_reverts_select_from_on_export():
    cc1 = BAREBONES_1
    cc2 = Content(cc1)
    row = Row(content=cc2, row={
        'type': 'select_one',
        '$anchor': 'xx',
        'select_from_list_name': 'xyz',
    })

    schema = '1'
    assert 'select_from' not in row.flat_export(schema=schema)
    assert 'select_from_list_name' in row.flat_export(schema=schema)


    schema = '2'
    assert 'select_from' in row.flat_export(schema=schema)
    assert 'select_from_list_name' not in row.flat_export(schema=schema)
    # pprint(row2schema1)


# def test_kfrozendict():
#     examp = kfrozendict({
#         'haslist': [
#             kfrozendict({
#                 'hasint': 123,
#             })
#         ],
#         'hastuple': (
#             kfrozendict({
#                 'hasstr': 'xyz',
#             }),
#         )
#     })
#     unfrozen = kfrozendict.unfreeze(examp)
#     assert isinstance(unfrozen, dict)
#     assert unfrozen['hastuple'][0]['hasstr'] == 'xyz'
