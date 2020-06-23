from a1d05eba1.content import Content
from a1d05eba1.utils.kfrozendict import kfrozendict

from pprint import pprint


CONTENT_1_NO_SETTINGS = {
    'schema': '1',
    'survey': [
        {'type': 'text',
          'name': 'v1',
          'label': ['abc'],
          },
      ],
}

CONTENT_1S = [
    CONTENT_1_NO_SETTINGS,
    {**CONTENT_1_NO_SETTINGS,
         'settings': [{}]},
    {**CONTENT_1_NO_SETTINGS,
         'settings': []},
]

CONTENT_1S_WITH_SETTINGS = [
    {**CONTENT_1_NO_SETTINGS,
         'settings': [{'title': 'aaa'}]},
    {**CONTENT_1_NO_SETTINGS,
         'settings': {'title': 'aaa'}},
]



def test_one2two():
    for cc in CONTENT_1S:
        content = Content(cc, exports_include_defaults=True)
        rr = content.export(schema='2')
        assert 'settings' in rr
        content = Content(cc, exports_include_defaults=False)
        rr = content.export(schema='2')
        assert 'settings' not in rr

    for cc in CONTENT_1S_WITH_SETTINGS:
        # don't delete valid settings
        content = Content(cc, exports_include_defaults=True)
        rr = content.export(schema='2')
        assert 'settings' in rr
        content = Content(cc, exports_include_defaults=False)
        rr = content.export(schema='2')
        assert 'settings' in rr
