from a1d05eba1.content import Content
from a1d05eba1.utils.kfrozendict import kfrozendict


CONTENT_1 = {
    'survey': [
        {'type': 'select_one',
            'select_from_list_name': 'xlistnamex',
            'name': 'q1',
            '$anchor': 'xxxxxxx',
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
    'settings': {'identifier': 'example',},
    'schema': '1',
}


CONTENT_2 = {
    'survey': [
        {'type': 'select_one',
            'select_from': 'xlistnamex',
            'name': 'q1',
            '$anchor': 'xxxxxxb',
            'label': {
                'tx0': 'mylabel',
            },
        },
        {'type': 'text',
            'name': 'show_if_q1_empty',
            '$anchor': 'xxxxxxc',
            'label': {
                'tx0': 'reason q1 is empty?',
            },
            'relevant': {
                'raw': '${q1} = \'\'',
            }}
    ],
    'choices': {
        'xlistnamex': [
            {'value': 'r1', 'label': {
             'tx0': 'r1',
            },
            '$anchor': 'xxxxxxd',
            },
            {'value': 'r2', 'label': {
             'tx0': 'r2',
            },
            '$anchor': 'xxxxxxe',
            },
            {'value': 'r3', 'label': {
             'tx0': 'r3',
            },
            '$anchor': 'xxxxxxf',
            },
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
        'identifier': 'example',
    },
    'schema': '2',
}


def test_one2two():
    result = Content(CONTENT_1).export(schema='2')
    assert 'translated' not in result

    label = result['survey'][0]['label']
    assert isinstance(label, dict)
    assert set(label.keys()) == set(['tx0'])
    assert isinstance(label['tx0'], str)

    tx1 = result['translations'][0]
    assert isinstance(tx1, dict)
    assert tx1 == {'$anchor':'tx0', 'name': '', 'default': True}
    assert isinstance(result['choices'], dict)
    assert len(result['choices'].keys()) > 0


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
        'schema': '1+kuid_anchor_key',
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
    exp2 = Content(exp).export(schema='1+kuid_anchor_key')
    assert '$kuid' in exp2['survey'][0]


def test_kfrozendict():
    kf1_0 = kfrozendict(abc=123)
    kf1_1 = kfrozendict(abc=123)
    kf2 = kfrozendict(abc=456)
    assert kf1_0 == kf1_1
    assert hash(kf1_0) == hash(kf1_1)
    assert repr(kf1_0) == '''<kfrozendict {'abc': 123}>'''
