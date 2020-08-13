import pytest

from a1d05eba1.utils.kfrozendict import kfrozendict
from a1d05eba1.exceptions import TranslationImportError
from a1d05eba1.components.translations import load_string

from a1d05eba1.content_variations import build_content


CONTENT_1 = {
    'survey': [
        {'type': 'text',
            '$anchor': 'x',
            'name': 'book',
            'label': ['The patient']
        },
    ],
    'translations': [
        'English (en)',
    ],
    'translated': [
        'label'
    ],
    'settings': {},
    'schema': '1',
}


def content1_to_tx(content):
    kk = build_content(content)
    return (kk.txs._tuple[0], kk)


def test_1_with_default_tx():
    content = build_content({
        'survey': [{'$anchor': 'x', 'type': 'text'}],
        'translations': [
            'English',
            'French',
        ],
        'settings': {
            'default_language': 'French',
        },
        'schema': '1',
    })
    assert content.txs[0].name == 'French'
    result = content.export_to('2')
    names = [
        tx.get('name') for tx in result['translations']
    ]
    assert names == ['French', 'English']


def test_1_with_tx_locales():
    aliases_for_french = [
        'French (fr)',
        'French',
        'fr',
    ]
    for dtx in aliases_for_french:
        content = build_content({
            'survey': [{'$anchor': 'x', 'type': 'text'}],
            'translations': [
                'English (en)',
                'French (fr)',
            ],
            'settings': {
                'default_language': dtx,
            },
            'schema': '1',
        })
        result = content.export_to('2')
        # verify order was changed
        assert content.txs.names == ['French', 'English']


def test_one2two():
    # ensure that the translations are imported correctly
    (tx1, kk) = content1_to_tx({
        'survey': [
            {
                'type': 'text',
                '$anchor': 'q1',
                'label': ['enlabelle'],
            }
        ],
        'translations': [
            'English (xxx)',
        ],
        'translated': [
            'label',
        ],
        'settings': {},
        'schema': '1',
    })
    assert tx1.locale == 'xxx'
    assert tx1.anchor == 'xxx'

    result = kk.export_to('2')
    assert result['translations'][0]['name'] == 'English'
    assert result['translations'][0]['locale'] == 'xxx'
    assert result['translations'][0]['$anchor'] == 'xxx'

def test_reorder_translations():
    cc = build_content({
        'survey': [
            {'type': 'text',
                'name': 'q1',
                '$anchor': 'x',
                'label': {
                    'en': 'en q1',
                    'fr': 'fr q1',
                }},
            {'type': 'text',
                '$anchor': 'y',
                'name': 'q2',
                'label': {
                    'en': 'en q2',
                    'fr': 'fr q2',
                }}
        ],
        'translations': [
            {'name': 'eng',
                '$anchor': 'en',
                'locale': 'en'},
            {'name': 'fr',
                'initial': True,
                '$anchor': 'fr',
                'locale': 'fr'}
        ],
        'settings': {},
        'schema': '2',
    })
    anchors_0 = [c.anchor for c in cc.txs]
    assert anchors_0 == ['fr', 'en']



def test_no_duplicate_translation_names():
    # because that would be confusing
    invalid_txpairs = [
        ['English', 'English'],
        ['', None],
        ['English (en)', 'English'],
        ['English', 'English (en)'],
    ]
    for invalid_txpair in invalid_txpairs:
        with pytest.raises(TranslationImportError):
            cc = build_content({
                'schema': '1',
                'survey': [{'$anchor': 'x', 'type': 'text'}],
                'translations': invalid_txpair,
            })


def test_schema_1_load_strings_method():
    expected_vals = [
        # preferred:
        ('English (en)',    'English', 'en'),
        # also found in "the wild":
        ('English(en)',     'English', 'en'),
        ('English  (en)',   'English', 'en'),
        ('English',         'English', None),
        # why not
        (' English ',       'English', None),
    ]

    for (fullname, ex_name, ex_locale) in expected_vals:
        _name, _locale = load_string(fullname)
        assert _name == ex_name
        assert _locale == ex_locale


def test_simple_xlsform():
    cc = build_content({
        'survey': [
            {'type': 'text', 'name': 'q1', 'label::En': 'Q 1', 'label::Fr': 'Qf 1'},
            {'type': 'select_one dogs', 'name': 'q2', 'label::En': 'Dog', 'label::Fr': 'Chien'},
        ],
        'choices': [
            {'list name': 'dogs',
             'name': 'poodle',
             'label::En': 'Poodle',
             'label::Fr': 'Poodelle',
             },
            {'list name': 'dogs',
             'name': 'labrador',
             'label::En': 'Labrador',
             'label::Fr': 'Labradour',
             }
        ],
    }, classname='X_Content')
    exp = cc.export()
    assert [tx['name'] for tx in exp['translations']] == ['En', 'Fr']
