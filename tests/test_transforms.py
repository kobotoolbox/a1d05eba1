import pytest

from a1d05eba1.content_variations import (
    build_content,
    V1_Content_Anchors,
    RemoveEmptiesRW,
)

from a1d05eba1.utils.kfrozendict import kfrozendict
from a1d05eba1.utils.kfrozendict import deepfreeze
from a1d05eba1.transformations.xlsform_translations import (
    XlsformTranslations,
    rw_inspect_content_translations,
    rw_mutate_content,
)

from a1d05eba1.transformations.flatten_survey_by_anchor import FlattenSurveyByAnchor

from a1d05eba1.exceptions import StructureError
from a1d05eba1.exceptions import DuplicateAnchorError
from a1d05eba1.exceptions import UnclosedGroupError
from a1d05eba1.exceptions import MismatchedBeginEndGroupError


NULL_TRANSLATION = 'NULL_TRANSLATION'

S1 = deepfreeze({
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


flatten_survey_by_anchor = FlattenSurveyByAnchor()

def test_flattener():
    result1 = flatten_survey_by_anchor.fw(S1)
    restored = flatten_survey_by_anchor.rw(result1)
    assert restored == S1


def test_reverser():
    content = deepfreeze({
        'survey': [
            {'label': 'abc',
             'label::English': 'xyz'}
        ]
    })
    ctx = rw_inspect_content_translations(content)
    content = kfrozendict.unfreeze(rw_mutate_content(content, ctx))

    row0 = content['survey'][0]
    assert 'label' in row0
    assert 'label::English' not in row0
    assert row0['label'] == ['abc', 'xyz']

    assert content['translations'] == [NULL_TRANSLATION, 'English']
    assert content['translated'] == ['label']

def test_xlsform_images():
    ctx = rw_inspect_content_translations(deepfreeze({
        'survey': [
            {'media::image::aa': 'abc',
             'media::image::zz': 'xyz'}
        ]
    }))
    assert 'media::image::aa' in ctx.tx_colnames
    assert 'media::image::zz' in ctx.tx_colnames
    assert ctx.translations == ['aa', 'zz']

    ctx = rw_inspect_content_translations(deepfreeze({
        'survey': [
            {'media::image': 'abc',
             'media::image::zz': 'xyz'}
        ]
    }))
    assert 'media::image' in ctx.tx_colnames
    assert 'media::image::zz' in ctx.tx_colnames
    assert ctx.translations == [NULL_TRANSLATION, 'zz']
    assert ctx.translated == {'image'}

def test_reverser_weird_col():
    cc = {'survey':[{'label::':'aa'}, {'label': 'bb'}]}
    ctx = rw_inspect_content_translations(cc)
    assert 'label' in ctx.translated
    cc = kfrozendict.freeze(cc)
    mut = rw_mutate_content(cc, ctx)
    row0 = mut['survey'][0]
    row1 = mut['survey'][1]
    # row1 and row0 should evaluate to the same translation
    assert row0['label'][0] == 'aa'
    assert row1['label'][0] == 'bb'

def test_colons_forward_empty_tx():
    cc = {'schema': '2',
         'survey': [{'$anchor': 'kd1btqqgz',
                     'label': {'tx0': 'state'},
                     'name': 'state',
                     'select_from': 'states',
                     'type': 'select_one'}],
         'translations': [{'$anchor': 'tx0', 'name': ''}]}
    result = build_content(cc).export_to('xlsform')
    row0 = result['survey'][0]
    assert 'label' in row0

def test_additional():
    cc = {'schema': '1+xlsform',
     'settings': [{'default_language': None}],
     'survey': [{'name': 'start', 'type': 'start'},
                {'name': 'end', 'type': 'end'},
                {'$anchor': 'ty7yd67',
                 'label': 'q1',
                 'required': False,
                 'type': 'text'},
                {'$anchor': 'pm4jk80',
                 'label': 'q2',
                 'required': False,
                 'type': 'integer'}],
        'choices': [],
    }
    content = build_content(cc)
    result = content.export_to('1')
    assert len(result['translations']) == 1
    assert result['translations'] == [None]

    content = build_content(cc)
    result = content.export_to('2')
    assert len(result['translations']) == 1
    assert result['translations'] == [{'$anchor': 'tx0', 'name': ''}]


def test_colons_forward():
    result = build_content({
        # 'schema': '1',
        'survey': [
            {'type': 'text', 'name': 'q1', '$anchor': 'q1', 'label': ['t1lab', 't2lab']},
            {'type': 'select_one',
                'name': 'q2',
                '$anchor': 'q2',
                'select_from_list_name': 'xyz',
                'label': ['s1lab', 's2lab'],
                'hint': ['q2hintt1', 'q2hintt2'],
            }
        ],
        'choices': [
            {'list_name': 'xyz', '$anchor': 'aaa', 'value':'val1', 'label': [
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
    }).export_to('xlsform')
    row0 = result['survey'][0]
    choice0 = result['choices'][0]
    assert 'label::T1' in row0
    assert 'label::T1' in choice0


def test_1_plus_colons():
    content = build_content({
        # '1+xx' equivalent to 'xlsform'
        'schema': '1',
        'survey': [
            {'type': 'text',
                'name': 'book',
                '$anchor': 'book',
                'label::English': 'The patient',
                'label::French': 'Le patient',
            },
        ],
        'settings': [{}],
    })
    result = content.export_to('1')
    row0 = result['survey'][0]
    assert row0['label'] == ['The patient', 'Le patient']

def test_alternative_colon_configs():
    content = build_content({
        'schema': '1+xlsform',
        'survey': [
            {'type': 'text',
                'name': 'book',
                '$anchor': 'book',
                'label: English': 'The patient',
                'label:French': 'Le patient',
            },
        ],
        'settings': [{}],
    })
    txs = content.export_to('2')['translations']
    txnames = [tx['name'] for tx in txs]
    assert txnames == ['English', 'French']

def test_split_types():
    content = build_content({
        'survey': [
            {
                'type': 'select_one dog',
                '$anchor': 'q1',
            }
        ],
        'settings': [],
    }, classname='X_Content')
    row0 = content.export_to('1')['survey'][0]
    assert row0['type'] == 'select_one'
    assert row0['select_from_list_name'] == 'dog'
    row0 = content.export_to('xlsform')['survey'][0]
    assert row0['type'] == 'select_one dog'

GRP_S1 = deepfreeze({
    'survey': [{'type': 'begin_group', '$anchor': 'grp_a'},
                {'type': 'note', '$anchor': 'note_a'},
                {'type': 'begin_group', '$anchor': 'grp_b'},
                {'type': 'text', '$anchor': 'text_b'},
                {'type': 'end_group', '$anchor': '/grp_b'},
                {'type': 'integer', '$anchor': 'int_a'},
                {'type': 'begin_group', '$anchor': 'grp_c'},
                {'type': 'text', '$anchor': 'text_c'},
                {'type': 'end_group', '$anchor': '/grp_c'},
                {'type': 'end_group', '$anchor': '/grp_a'},
                {'type': 'integer', '$anchor': 'int_z'},
                ]
})


class V1_Content_NoValidate(V1_Content_Anchors):
    input_schema = None
    def __init__(self, *args, **kwargs):
        self.transformers = self.transformers + (RemoveEmptiesRW,)
        super().__init__(*args, **kwargs)

def test_remove_empties():
    cc = V1_Content_NoValidate({
        'survey': [
            {'type': 'text', '$anchor': 'anchor'},
            {},
            {'type': 'text', '$anchor': 'anchor2'},
            {},
            {'type': 'text', '$anchor': 'anchor3'},
        ],
        'choices': [
            {'list_name': 'aa',
                '$anchor': 'a4',
                'value': 'aaa'},
            {'list_name': 'aa',
                '$anchor': 'a5',
                'value': 'aab'},
            {'list_name': 'aa',
                '$anchor': 'a6',
                'value': 'aac'},
        ],
        # 'settings': [],
        'translations': [None],
    })
    result = cc.export_to('xlsform')
    assert len(result['survey']) == 3
    assert len(result['choices']) == 3

def test_create_single_translation():
    cc = build_content({
        'schema': '1',
        'survey': [
            {'type': 'text', '$anchor': 'x', 'label': 'q1'},
        ],
        'choices': [
            {'list_name': 'xx', 'value': 'l1v1', '$anchor': 'y', 'label': 'label 1'},
            {'list_name': 'xx', 'value': 'l1v2', '$anchor': 'z', 'label': 'label 2'},
        ],
        'translations': [None],
    }, classname='V1_Content_Anchors')
    result = cc.export_to('2')
    assert len(result['translations']) == 1
    result = cc.export_to('1')
    assert result['translated'] == ['label']

def test_unique_anchors():
    with pytest.raises(DuplicateAnchorError):
        cc = build_content({
            'schema': '2',
            'survey': [
                # same "$anchor" but different "name"
                {'$anchor': 'x',
                 'name': 'q1',
                 'label': {'tx0': 'q1'}, 'type': 'text',
                    },
                {'$anchor': 'x',
                 'name': 'q2',
                 'label': {'tx0': 'q2'}, 'type': 'text',
                    },
            ],
            'choices': {'xx': [{'$anchor': 'x',
                             'label': {'tx0': 'label 1'},
                             'value': 'l1v1'}]},
            'translations': [{'$anchor': 'tx0', 'name': ''}]
         })

def test_unmatched_group_1():
    with pytest.raises(StructureError):
        cc = build_content({
            'schema': '2',
            'survey': [
                {'$anchor': 'a', 'type': 'begin_group'},
                {'$anchor': 'b', 'type': 'text'},
            ],
            'translations': [{'$anchor': 'tx0', 'name': ''}]
         })

def test_unmatched_group_2():
    with pytest.raises(StructureError):
        cc = build_content({
            'schema': '2',
            'survey': [
                {'$anchor': 'a', 'type': 'begin_group'},
                {'$anchor': 'b', 'type': 'text'},
                {'$anchor': 'c', 'type': 'end_group'},
                {'$anchor': 'd', 'type': 'end_group'},
            ],
            'translations': [{'$anchor': 'tx0', 'name': ''}]
         })


def test_formpack_schema_to_lists():
    # with pytest.raises(ValueError):
    kontent = {'choices': [{'label': ['French'],
              'list_name': 'al1hv46',
              'name': 'french',
              'order': 0},
             {'label': ['Italian'],
              'list_name': 'al1hv46',
              'name': 'italian',
              'order': 1},
             {'label': ['American'],
              'list_name': 'al1hv46',
              'name': 'american',
              'order': 2}],
              # how did this pass before?
              'translations': ['En'],
 'survey': [{'label': ['Favorite coffee type'],
             'name': 'favorite_coffee_type',
             'required': False,
             'select_from_list_name': 'al1hv46',
             'type': 'select_multiple'},
            {'label': ['Brand of coffee machine'],
             'name': 'brand_of_coffee_machine',
             'required': False,
             'type': 'text'}],
             'schema': '1+formpack'}
    cc = build_content(kontent)
    result = cc.export_to('2')
    s0, s1 = result['survey']
    assert isinstance(s0['label'], dict)
    assert set(iter(s0['label'].keys())) == {'tx0'}

#
# def test_weird_lists():
#     content_str = '''
#     {
#   "choices": [
#     {
#       "name": "french",
#       "label": [
#         "French"
#       ],
#       "list_name": "al1hv46",
#       "order": 0
#     },
#     {
#       "name": "italian",
#       "label": [
#         "Italian"
#       ],
#       "list_name": "al1hv46",
#       "order": 1
#     },
#     {
#       "name": "american",
#       "label": [
#         "American"
#       ],
#       "list_name": "al1hv46",
#       "order": 2
#     }
#   ],
#   "survey": [
#     {
#       "select_from_list_name": "al1hv46",
#       "required": false,
#       "label": [
#         "Favorite coffee type"
#       ],
#       "name": "favorite_coffee_type",
#       "type": "select_multiple"
#     },
#     {
#       "required": false,
#       "type": "text",
#       "label": [
#         "Brand of coffee machine"
#       ],
#       "name": "brand_of_coffee_machine"
#     }
#   ]
# }
#     '''
#     import json
#     cobj = json.loads(content_str)
#     import ipdb; ipdb.set_trace()
