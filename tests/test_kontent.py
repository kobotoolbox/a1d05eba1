from a1d05eba1.content import Content
from a1d05eba1.utils.kfrozendict import kfrozendict

from pprint import pprint


CONTENT_1 = {
    'survey': [
        {'type': 'select_one',
            'select_from_list_name': 'xlistnamex',
            'name': 'q1',
            'label': [
                'label'
            ]
        },
    ],
    'choices': [
        {'list_name': 'xlistnamex', 'name': 'r1', 'label': ('r1',)},
        {'list_name': 'xlistnamex', 'name': 'r2', 'label': ['r2']},
        {'list_name': 'xlistnamex', 'name': 'r3', 'label': ['r3']},
    ],
    'translations': [
        None
    ],
    'translated': [
        'label'
    ],
    'settings': {'id_string': 'example',},
    'schema': '1',
}


CONTENT_2 = {
    'survey': [
        {'type': 'select_one',
            'select_from': 'xlistnamex',
            'name': 'q1',
            'label': {
                'tx0': {
                    'string': 'mylabel'
                },
            },
        },
        {'type': 'text',
            'name': 'show_if_q1_empty',
            'label': {
                'tx0': {
                    'string': 'reason q1 is empty?',
                }
            },
            'relevant': {
                'string': '${q1} = \'\'',
            }}
    ],
    'choices': {
        'xlistnamex': [
            {'name': 'r1', 'label': {
            'tx0': {
                'string': 'r1',
            }
            }},
            {'name': 'r2', 'label': {
            'tx0': {
                'string': 'r2',
            }
            }},
            {'name': 'r3', 'label': {
            'tx0': {
                'string': 'r3',
            }
            }},
        ],
    },
    'translations': [
        {
            'name': 'eng',
            '$anchor': 'tx0',
            'locale': 'en',
        }
    ],
    'settings': {
        'id_string': 'example',
    },
    'schema': '2',
}


def test_one2two():
    result = Content(CONTENT_1).export(schema='2')
    assert 'translated' not in result

    label = result['survey'][0]['label']
    assert isinstance(label, dict)
    assert set(label.keys()) == set(['tx0'])
    assert isinstance(label['tx0'], dict)
    assert set(label['tx0'].keys()) == set(['string'])

    tx1 = result['translations'][0]
    assert isinstance(tx1, dict)
    assert tx1 == {'$anchor':'tx0', 'name': None, 'default': True}
    assert isinstance(result['choices'], dict)
    assert len(result['choices'].keys()) > 0


def test_generate_anchors():
    def get_row0s(surv):
        row0 = surv['survey'][0]
        if isinstance(surv['choices'], list):
            return (row0, surv['choices'][0])
        return (row0, surv['choices']['xlistnamex'][0])

    for _gen in [True, False]:
        # generate_anchors=True/False
        for content in [CONTENT_1, CONTENT_2]:
            # content.export(schema='1'/'2')
            for cs in ['1', '2']:
                akey = '$anchor' if (cs == '2') else '$kuid'
                result = Content(content,
                                 generate_anchors=_gen
                                 ).export(schema=cs)
                if not _gen:
                    assert akey not in result['survey'][0]
                else:
                    (row0, choice0) = get_row0s(result)
                    assert akey in row0
                    assert akey in choice0
                    asval1 = row0[akey]
                    acval1 = choice0[akey]
                    for cs2 in ['1', '2']:
                        # ensure anchor is preserved on second pass
                        result_x = Content(result,
                                           generate_anchors=True
                                           ).export(schema=cs2)
                        akey = '$anchor' if (cs2 == '2') else '$kuid'
                        (row0, choice0) = get_row0s(result_x)

                        # survey[n]['$anchor'] does not get changed on pass 2
                        asval2 = row0[akey]
                        assert asval1 == asval2

                        # choices[...]['$anchor'] does not get changed on pass 2
                        acval2 = choice0[akey]
                        assert acval1 == acval2


def test_one2one():
    result = Content(CONTENT_1).export(schema='1')

    assert 'translated' in result
    label = result['survey'][0]['label']
    assert isinstance(label, list)
    assert len(label) == 1
    tx1 = result['translations'][0]
    assert tx1 == None
    assert isinstance(result['choices'], list)
    assert len(result['choices']) > 0


def test_two2one():
    result = Content(CONTENT_2).export(schema='1')
    assert 'translated' in result
    label = result['survey'][0]['label']
    assert isinstance(label, list)
    assert len(label) == 1
    assert label[0] == 'mylabel'
    tx1 = result['translations'][0]
    assert tx1 == 'eng (en)'


def test_two2two():
    result = Content(CONTENT_2).export(schema='2')
    assert 'translated' not in result
    label = result['survey'][0]['label']
    assert isinstance(label, dict)
    assert set(label.keys()) == set(['tx0'])
    tx1 = result['translations'][0]
    assert isinstance(tx1, dict)
    assert tx1 == {'$anchor':'tx0', 'name':'eng', 'locale': 'en', 'default': True}
    row2 = result['survey'][1]
    assert 'name' in row2


def test_rename_kuid_to_anchor():
    cc = Content({
        'schema': '1',
        'survey': [
            {'type': 'text',
                'label': ['asdf'],
                '$kuid': 'asdfasdf'}
        ],
        'translations': [None],
        'translated': ['label'],
        'settings': {},
    })
    exp = cc.export(schema='2')
    assert '$anchor' in exp['survey'][0]
    # and rename it back to '$kuid' when saved as schema='1'
    exp2 = Content(exp).export(schema='1')
    assert '$kuid' in exp2['survey'][0]
