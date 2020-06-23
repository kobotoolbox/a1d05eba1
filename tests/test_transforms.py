from a1d05eba1.content import Content
# from a1d05eba1.row import Row
# from a1d05eba1.choices import Choice

from a1d05eba1.utils.kfrozendict import kfrozendict
from a1d05eba1.transformations.flattened_translations import (
    rw,
    fw,
    inspect_content_translations,
    mutate_content,
)

from a1d05eba1.transformations import flatten_survey_by_anchor


S1 = kfrozendict.freeze({
    'survey': [
        {'$anchor':'aaa','value':'111'},
        {'$anchor':'bbb','value':'222'},
        {'$anchor':'333','value':'333'},
    ],
    'choices': {
        'xa': [
            {'$anchor':'xxaa11','value':'xa1 aaa'},
            {'$anchor':'xxaa22','value':'xa2 bbb'},
            {'$anchor':'xxaa33','value':'xa3 ccc'},
        ],
        'xb': [
            {'$anchor':'xxbb11','value':'xb1 aaa'},
            {'$anchor':'xxbb22','value':'xb2 bbb'},
            {'$anchor':'xxbb33','value':'xb3 ccc'},
        ],
    }
})


def test_flattener():
    result1 = flatten_survey_by_anchor.fw(S1)
    restored = flatten_survey_by_anchor.rw(result1)
    assert restored == S1


def test_reverser():
    content = kfrozendict.freeze({
        'survey': [
            {'label': 'abc',
             'label::English': 'xyz'}
        ]
    })
    ctx = inspect_content_translations(content)
    content = kfrozendict.unfreeze(mutate_content(content, ctx))

    row0 = content['survey'][0]
    assert 'label' in row0
    assert 'label::English' not in row0
    assert row0['label'] == ['abc', 'xyz']

    assert content['translations'] == [None, 'English']
    assert content['translated'] == ['label']


def test_additional():
    cc = {'schema': '1::',
     'settings': [{'default_language': None}],
     'survey': [{'name': 'start', 'type': 'start'},
                {'name': 'end', 'type': 'end'},
                {'$kuid': 'ty7yd67',
                 'label': 'q1',
                 'required': False,
                 'type': 'text'},
                {'$kuid': 'pm4jk80',
                 'label': 'q2',
                 'required': False,
                 'type': 'integer'}]}
    content = Content(cc)
    result = content.export(schema='1')
    assert len(result['translations']) == 1
    assert result['translations'] == [None]

    content = Content(cc)
    result = content.export(schema='2')
    assert len(result['translations']) == 1
    assert result['translations'] == [{'$anchor': 'tx0', 'default': True,
                                       'name': ''}]


def test_colons_forward():
    result = Content({
        'schema': '1',
        'survey': [
            {'type': 'text', 'name': 'q1', 'label': ['t1lab', 't2lab']},
            {'type': 'select_one',
                'name': 'q2',
                'select_from_list_name': 'xyz',
                'label': ['s1lab', 's2lab'],
                'hint': ['q2hintt1', 'q2hintt2'],
            }
        ],
        'choices': [
            {'list_name': 'xyz', 'value':'val1', 'label': [
                'c1lab',
                'c2lab',
            ]}
        ],
        'translations': [
            'T1', 'T2',
        ],
        'settings': {},
        'translated': [
            'label',
            'hint',
        ]
    }).export(schema='xlsform')
    row0 = result['survey'][0]
    choice0 = result['choices'][0]
    assert 'label::T1' in row0
    assert 'label::T1' in choice0


def test_1_plus_colons():
    content = Content({
        # '1+xx' equivalent to 'xlsform'
        'schema': '1+::',
        'survey': [
            {'type': 'text',
                'name': 'book',
                'label::English': 'The patient',
                'label::French': 'Le patient',
            },
        ],
        'translated': [
            'label'
        ],
        'settings': {},
    })
    result = content.export(schema='1')
    row0 = result['survey'][0]
    assert row0['label'] == ['The patient', 'Le patient']
