from a1d05eba1.content import Content

def test_list_space_name():
    cc = Content({
        'schema': 'xlsform',
        'survey': [],
        'choices': [
            {'list name': 'xx',
                'value': 'yy',
                'label': 'yy'},
            {'list name': 'xx',
                'value': 'zz',
                'label': 'zz'},
        ]
    })
    result = cc.export(schema='2')
    assert len(result['choices']) == 1
    assert 'xx' in result['choices']


def test_metas_and_settings():
    cc = Content({
        'schema': 'xlsform',
        'settings': [
            {'formid': 'mynewform'}
        ],
        'survey': [
            {'type': 'start', 'name': 'start',
            '$anchor': '$start',},
            {'type': 'end', 'name': 'end',
            '$anchor': '$end',},
        ],
    })
    result = cc.export(schema='2')
    assert 'metas' in result['settings']
