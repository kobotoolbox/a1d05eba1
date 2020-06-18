from a1d05eba1.content import Content
from a1d05eba1.utils.kfrozendict import kfrozendict


CONTENT = {
    'schema': '1',
    'survey': [
        {'type': 'start',
            'name': 'start',
        },
        {'type': 'end',
            'name': 'end',
        },
    ],
    'translations': [
        None
    ],
    'translated': [
        'label'
    ],
    'settings': {},
}


def test_extract_metas_properly():
    # just converts back and forth and back and forth
    # verifies settings.metas is correct
    result_2 = Content(CONTENT).export(schema='2')

    assert len(result_2['survey']) == 0
    assert 'settings' in result_2
    assert 'metas' in result_2['settings']

    result_21 = Content(result_2).export(schema='1')
    assert len(result_21['survey']) == 2
    assert 'metas' not in result_21['settings']

    result_22 = Content(result_2).export(schema='2')
    result_221 = Content(result_22).export(schema='1')

    assert len(result_221['survey']) == 2
    assert 'metas' not in result_221['settings']

    result_2212 = Content(result_221).export(schema='2')
    assert len(result_2212['survey']) == 0
    assert result_2212['settings']['metas'] == {'start': True, 'end': True}
