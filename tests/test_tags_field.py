from a1d05eba1.content import Content
from a1d05eba1.utils import kfrozendict

from a1d05eba1.special_fields.tags import _expand_tags

CONTENT_1 = {
    'schema': '1',
    'translations': [
        'My Tx (mytx)'
    ],
    'survey': [],
}

CONTENT_2 = {
    'schema': '2',
    'translations': [
        {'$anchor': 'tx0', 'name': ''},
    ],
}

def test_import_hxl_tags_from_string1():
    result = Content({**CONTENT_1, 'survey': [
        {'type': 'text',
         '$anchor': 'q1',
         'hxl': '#loc+name #foo+bar'},
    ]}).export(schema='2')

    row0 = result['survey'][0]
    assert row0['tags'] == ['hxl:#loc', 'hxl:+name', 'hxl:#foo', 'hxl:+bar']

def test_import_hxl_tags_from_string1_plus_tags():
    result = Content({**CONTENT_1, 'survey': [
        {'type': 'text',
         '$anchor': 'q1',
         'hxl': '#loc+name',
         'tags': 'hxl:#foo'}
    ]}).export(schema='2')

    row0 = result['survey'][0]
    tags0 = row0['tags']
    assert tags0 == ['hxl:#foo', 'hxl:#loc', 'hxl:+name']

def test_import_hxl_tags_from_string2():
    result = Content({**CONTENT_2, 'survey': [
        {'type': 'text',
         '$anchor': 'q1',
         'tags': ['hxl:#foo', 'hxl:#loc', 'hxl:+name']}
    ]}).export(schema='1')

    row0 = result['survey'][0]
    assert 'tags' not in row0
    tags0 = row0['hxl']
    assert tags0 == '#foo #loc +name'

def test_import_hxl_tags_from_string2_plus_tags():
    result = Content({**CONTENT_2, 'survey': [
        {'type': 'text',
         '$anchor': 'q1',
         'tags': ['hxl:#foo', 'hxl:#loc', 'hxl:+name', 'misc']}
    ]}).export(schema='1')

    row0 = result['survey'][0]
    # assert 'hxl' not in row0
    tags0 = row0['hxl']
    assert row0['tags'] == 'misc'
    assert tags0 == '#foo #loc +name'

def test_tags_validate():
    cc = Content({**CONTENT_2, 'survey': [
        {'type': 'text',
         '$anchor': 'q1',
         'tags': ['hxl:#foo', 'hxl:#loc', 'hxl:+name', 'misc']}
    ]}, perform_validation=True)

def test_expand_tags_method():
    def _expand(tag_str, existing_tags=None):
        params = {'hxl': tag_str}
        if existing_tags:
            params['tags'] = existing_tags
        return sorted(_expand_tags(**params))

        row = kfrozendict.freeze(row)
    expected = sorted(['hxl:#tag1', 'hxl:+attr1', 'hxl:+attr2'])
    assert expected == _expand('#tag1+attr1+attr2')
    assert expected == _expand(' #tag1 +attr1 +attr2 ')
    assert expected == _expand(' #tag1 +attr1 ', ['hxl:+attr2'])
    test_underscores = ['#tag_underscore', '+attr_underscore']
    expected = ['hxl:' + x for x in test_underscores]
    assert expected == _expand(''.join(test_underscores))
