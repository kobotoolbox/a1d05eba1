from a1d05eba1.content import Content
from a1d05eba1.utils.kfrozendict import kfrozendict

from pprint import pprint


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


def content2tx(content):
    kk = Content(content)
    return (kk.txs._tuple[0], kk)


def test_1_with_no_default_tx():
    content = Content({
        'survey': [],
        'translations': [
            'English',
        ],
        'settings': {},
        'schema': '1',
    })
    result = content.export(schema='2')
    defaults = [
        tx.get('default') for tx in result['translations']
    ]
    assert defaults == [True]


def test_1_with_default_tx():
    content = Content({
        'survey': [],
        'translations': [
            'English',
            'French',
        ],
        'settings': {
            'default_language': 'French',
        },
        'schema': '1',
    })
    result = content.export(schema='2')
    defaults = [
        tx.get('default') for tx in result['translations']
    ]
    assert defaults == [None, True]


def test_1_with_tx_locales():
    content = Content({
        'survey': [],
        'translations': [
            'English (en)',
            'French (fr)',
        ],
        'settings': {
            'default_language': 'French (fr)',
        },
        'schema': '1',
    })
    result = content.export(schema='2')
    result2 = Content(result).export(schema='1')
    defaults = [
        tx.get('default') for tx in result['translations']
    ]
    assert defaults == [None, True]


def test_one2two():
    # ensure that the translations are imported correctly
    (tx1, kk) = content2tx({
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

    result = kk.export(schema='2')
    assert result['translations'][0]['name'] == 'English'
    assert result['translations'][0]['locale'] == 'xxx'
    assert result['translations'][0]['$anchor'] == 'xxx'

def test_reorder_translations():
    cc = Content({
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
                '$anchor': 'fr',
                'default': True,
                'locale': 'fr'}
        ],
        'settings': {},
        'schema': '2',
    })
    anchors_0 = [c.anchor for c in cc.txs]
    assert anchors_0 == ['en', 'fr']
    cc.txs.reorder()
    anchors_1 = [c.anchor for c in cc.txs]
    assert anchors_1 == ['fr', 'en']
