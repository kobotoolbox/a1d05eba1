from a1d05eba1.content import Content
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
    result = Content({**CONTENT_1, 'survey': [
        {'type': 'integer',
            'name': 'age',
            '$anchor': 'age',
            'label': ['label'],
            'constraint': '${age} > 0 and ${age} < 120',
            'constraint_message': ['that is not a valid age']}
    ]}).export(schema='2')

    row0 = result['survey'][0]
    constraint1 = row0['constraint']

    assert constraint1 == {
            'string': '${age} > 0 and ${age} < 120',
            'message': {'mytx': {'string': 'that is not a valid age'}},
    }

    result2 = Content(result).export(schema='1')
    row0 = result2['survey'][0]
    # {'constraint': '${age} > 0 and ${age} < 120',
    #  'constraint_message': ['that is not a valid age'],
    #  'label': ['label'],
    #  'name': 'age',
    #  'type': 'integer'}
    assert row0['constraint'] == '${age} > 0 and ${age} < 120'
    assert row0['constraint_message'][0] == 'that is not a valid age'
