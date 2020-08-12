from a1d05eba1.content_variations import build_content
from a1d05eba1.utils.kfrozendict import kfrozendict


CONTENT_1 = {
    'schema': '1',
    'translations': [
        'My Tx (mytx)'
    ],
    'translated': [
        'label',
        'constraint_message',
    ],
    'settings': {},
}


def test_import_constraint_with_message_from_1():
    result = build_content({**CONTENT_1, 'survey': [
        {'type': 'integer',
            'name': 'age',
            '$anchor': 'age',
            'label': ['label'],
            'constraint': '${age} > 0 and ${age} < 120',
            'constraint_message': ['that is not a valid age']}
    ]}).export_to('2')

    row0 = result['survey'][0]
    constraint1 = row0['constraint']

    assert constraint1 == {
            'string': '${age} > 0 and ${age} < 120',
            'message': {'mytx': 'that is not a valid age'},
    }

    result2 = build_content(result).export_to('1')
    row0 = result2['survey'][0]
    # {'constraint': '${age} > 0 and ${age} < 120',
    #  'constraint_message': ['that is not a valid age'],
    #  'label': ['label'],
    #  'name': 'age',
    #  'type': 'integer'}
    assert row0['constraint'] == '${age} > 0 and ${age} < 120'
    assert row0['constraint_message'][0] == 'that is not a valid age'
