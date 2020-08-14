from a1d05eba1.content_variations import build_content


def test_list_space_name():
    cc = build_content({
        'schema': '1',
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
    result = cc.export_to('2')
    assert len(result['choices']) == 1
    assert 'xx' in result['choices']


def test_metas_and_settings():
    cc = build_content({
        'schema': '1',
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
    result = cc.export_to('2')
    assert 'metas' not in result['settings']
    assert 'metas' in result
