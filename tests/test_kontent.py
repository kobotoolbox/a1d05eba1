from a1d05eba1.content_variations import build_content
from a1d05eba1.content_variations import X_Content

from a1d05eba1.utils.kfrozendict import kfrozendict
from a1d05eba1.utils.kfrozendict import deepfreeze

# No anchors
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
    'settings': {'identifier': 'example',},
}

# V2, with anchors
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
}


def test_one2two():
    result = build_content(CONTENT_1).export_to('2')
    assert 'translated' not in result

    label = result['survey'][0]['label']
    assert isinstance(label, dict)
    assert set(label.keys()) == set(['tx0'])
    assert isinstance(label['tx0'], str)

    tx1 = result['translations'][0]
    assert isinstance(tx1, dict)
    assert tx1 == {'$anchor':'tx0', 'name': ''}
    assert isinstance(result['choices'], dict)
    assert len(result['choices'].keys()) > 0


def test_one2one():
    result = build_content(CONTENT_1).export_to('koboxlsform')
    assert 'translated' in result
    label = result['survey'][0]['label']
    assert isinstance(label, list)
    assert len(label) == 1
    tx1 = result['translations'][0]
    assert tx1 == None
    assert isinstance(result['choices'], list)
    assert len(result['choices']) > 0


def test_two2one():
    result = build_content(CONTENT_2).export_to('1')
    assert 'translated' in result
    label = result['survey'][0]['label']
    assert isinstance(label, list)
    assert len(label) == 1
    assert label[0] == 'mylabel'
    tx1 = result['translations'][0]
    assert tx1 == 'eng (en)'


def test_two2two():
    result = build_content(CONTENT_2).export_to('2')
    assert 'translated' not in result
    label = result['survey'][0]['label']
    assert isinstance(label, dict)
    assert set(label.keys()) == set(['tx0'])
    tx1 = result['translations'][0]
    assert isinstance(tx1, dict)
    assert tx1 == {'$anchor':'tx0', 'name':'eng', 'locale': 'en'}
    row2 = result['survey'][1]
    assert 'name' in row2

def test_rename_kuid_to_anchor():
    cc = build_content({
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
    exp2 = build_content(exp).export_to('xlsform')
    assert '$anchor' in exp2['survey'][0]


def test_kfrozendict():
    kf1_0 = kfrozendict(abc=123)
    kf1_1 = kfrozendict(abc=123)
    assert kf1_0 == kf1_1
    assert hash(kf1_0) == hash(kf1_1)
    assert repr(kf1_0) == '''<kfrozendict {'abc': 123}>'''

def test_kfrozendict_utility_methods():
    is_frozen = lambda dd: isinstance(dd, kfrozendict)
    is_not_frozen = lambda dd: isinstance(dd, dict)

    ex1 = kfrozendict(abc=123)
    ex1_unfrozen = ex1.unfreeze()
    assert is_not_frozen(ex1_unfrozen)

    ex1_unfrozen2 = kfrozendict.unfreeze(ex1)
    assert is_not_frozen(ex1_unfrozen2)

    ex2 = deepfreeze({'abc': 123})
    assert is_frozen(ex2)

    ex3 = kfrozendict({'abc': {'def': {'ghi': 999}}})
    assert is_not_frozen(ex3['abc'])
    assert is_not_frozen(ex3['abc']['def'])
    assert ex3['abc']['def']['ghi'] == 999

    ex3f = ex3.freeze()
    assert is_frozen(ex3f['abc'])
    assert is_frozen(ex3f['abc']['def'])
    assert ex3f['abc']['def']['ghi'] == 999


def test_image_alias_imports_translations():
    cc = X_Content({
        'survey': [
            {'type': 'text',
                'media::image::aa': 'my_image_aa.jpg',
                'media::image': 'my_image_nolang.jpg',
                '$anchor': 'moo',
                'name': 'name'},
        ],
        'choices': [],
        'settings': [],
    })
    ex = cc.export_to('2')
    assert ex['survey'][0]['image'] == {'tx0': 'my_image_nolang.jpg',
                                        'tx1': 'my_image_aa.jpg'}
