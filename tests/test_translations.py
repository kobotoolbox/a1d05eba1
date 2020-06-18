from a1d05eba1.content import Content
from a1d05eba1.utils.kfrozendict import kfrozendict


CONTENT_1 = {
    'survey': [
        {'type': 'text',
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
                'label': {
                    'en': {'string': 'en q1'},
                    'fr': {'string': 'fr q1'}
                }},
            {'type': 'text',
                'name': 'q2',
                'label': {
                    'en': {'string': 'en q2'},
                    'fr': {'string': 'fr q2'}
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

def test_aliases():
    cc = Content({'schema': '2',
        'settings': {},
        'survey': [],
        'translations': [
        {'name': 't1',
            'code': 't1'}
    ]})
    assert cc.export(schema='2')['translations'][0] == {'name': 't1', 'default': True, '$anchor': 't1'}

    cc = Content({'schema': '2',
        'settings': {},
        'survey': [],
        'translations': [
        {'name': 't1',
            'uicode': 'en',
            'code': 't1'}
    ]})
    assert cc.export(schema='2')['translations'][0] == {'name': 't1', 'default': True, '$anchor': 't1', 'locale': 'en'}
