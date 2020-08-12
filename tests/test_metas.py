from a1d05eba1.content_variations import build_content
from a1d05eba1.utils.kfrozendict import kfrozendict
from .common_utils import buncha_times


CONTENT = {
    'schema': '1',
    'survey': [
        {'type': 'start',
            '$anchor': '$start',
            'name': 'start',
        },
        {'type': 'end',
            '$anchor': '$end',
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

BASIC_1 = {
    'schema': '1',
    'translations': [None],
    'settings': {},
}

BASIC_2 = {
    'schema': '2',
    'translations': [{'name':'', '$anchor': 'xx'}],
    'settings': {},
}


def test_extract_metas_properly():
    # just converts back and forth and back and forth
    # verifies settings.metas is correct
    result_2 = build_content(CONTENT).export()

    assert len(result_2['survey']) == 0
    assert 'settings' in result_2
    assert 'metas' in result_2
    assert result_2['metas'] == {'start': True, 'end': True}

    cr2 = build_content(result_2)
    result_21 = cr2.export_to('1')
    assert cr2.metas.any()
    assert len(result_21['survey']) == 2
    assert 'metas' not in result_21['settings']

    result_22 = build_content(result_2).export_to('2')
    result_221 = build_content(result_22).export_to('xlsform')

    assert len(result_221['survey']) == 2
    assert 'metas' not in result_221['settings']

    for row in result_221['survey']:
        _type = row['type']
        row['$anchor'] = f'${_type}'
    result_221['translations'] = []
    result_2212 = build_content(result_221).export_to('2')
    assert len(result_2212['survey']) == 0
    assert result_2212['metas'] == {'start': True, 'end': True}


def test_tagged_metas():
    # baseline works
    cc = build_content({
        'schema': '2',
        'survey': [],
        'metas': {
            'start': True
        },
        'settings': {},
        'translations': [],
    }, validate=True)
    res = cc.export_to('1')
    assert cc.metas.any()
    assert 'metas' not in res['settings']
    assert res['survey'][0]['type'] == 'start'

    # hxl tags work
    cc = build_content({
        'schema': '2',
        'survey': [],
        'settings': {},
        'metas': {
            'start': {
                # 'torgs': 'aaaasdfasdfasdfasdf',
                'tags': ['hxl:#foo', 'hxl:+bar'],
            }
        },
        'translations': [],
    }, validate=True)
    row0 = cc.export_to('1')['survey'][0]
    assert row0['type'] == 'start'
    assert row0['name'] == 'start'
    assert row0['hxl'] == '#foo +bar'


def test_tagged_metas_content_1():
    # baseline works
    cc = build_content({
        'schema': '1',
        'survey': [
            {'type': 'start',
              'name': 'start',}
        ],
        'translations': [],
    }, validate=True)
    res = cc.export_to('2')
    assert 'metas' not in res['settings']
    assert res['metas']['start'] == True

    cc = build_content({
        'schema': '1',
        'survey': [
            {'type': 'start',
              'hxl': '#foo+baz',
              'name': 'start',}
        ],
        'translations': ['english'],
    }, validate=True)
    res = cc.export_to('2')
    _start_meta = res['metas']['start']
    assert _start_meta == {'tags': ['hxl:#foo', 'hxl:+baz']}

    cc2 = build_content(res)
    res = cc2.export_to('2')
    _start_meta = res['metas']['start']
    assert _start_meta == {'tags': ['hxl:#foo', 'hxl:+baz']}

    cc3 = build_content(res)
    res = cc3.export_to('xlsform')
    assert not isinstance(res['choices'], dict)
    _start_row = res['survey'][0]
    assert _start_row == {'name': 'start', 'type': 'start', 'hxl': '#foo +baz'}

    cc4 = build_content(res)
    res = cc4.export_to('xlsform')
    _start_row = res['survey'][0]
    assert _start_row == {'name': 'start', 'type': 'start', 'hxl': '#foo +baz'}

    cc5 = build_content(res)
    res = cc5.export_to('2')
    _start_meta = res['metas']['start']
    assert _start_meta == {'tags': ['hxl:#foo', 'hxl:+baz']}


def test_metas_overandover():
    '''
    tests a barebones survey content in schema 1 and schema 2 with
    the simplest value for the 'parameters'/'params' field
    '''
    basic = {**BASIC_1, 'survey': [
            {'type': 'start',
                '$anchor': 'xx',
                'name': 'start',},
            {'type': 'end',
                '$anchor': 'yy',
                'name': 'end',},
        ]}

    basic_2 = {**BASIC_2, 'survey': [],
            'metas': {'start': True, 'end': True}}

    kwargs = {
        'each': [basic, basic_2],
        'validate': True,
    }

    for (content, ctx) in buncha_times(**kwargs):
        surv = content['survey']
        if ctx.schema == '1':
            assert len(surv) == 2
        elif ctx.schema == '2':
            assert 'metas' in content
            assert len(content['metas']) == 2
