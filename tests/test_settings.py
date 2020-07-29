from a1d05eba1.content import Content
from a1d05eba1.utils.kfrozendict import kfrozendict

from pprint import pprint


CONTENT_1_NO_SETTINGS = {
    'schema': '1',
    'survey': [
        {'type': 'text',
          'name': 'v1',
          '$anchor': 'x',
          'label': ['abc'],
          },
      ],
     'translations': [''],
     'translated': ['label'],
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
        content = Content(cc)
        rr = content.export(schema='2', remove_nulls=False)
        assert 'settings' in rr
        rr = content.export(schema='2', remove_nulls=True)
        assert 'settings' not in rr

    for cc in CONTENT_1S_WITH_SETTINGS:
        # don't delete valid settings
        content = Content(cc)
        rr = content.export(schema='2', remove_nulls=False)
        assert 'settings' in rr
        content = Content(cc)
        rr = content.export(schema='2', remove_nulls=True)
        assert 'settings' in rr


PUBLIC_KEY_LINES = [
    'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyS/Dv8BKjM1K8ieLGg1E',
    'kWFcdVtMe2wRkdrtudg0dcuo/ucIQh6j7LJ6BdnWIndFhrF70BipWg2jXXsS6soR',
    'Wlm/Nd7uHeZDwxg6anSSjDlSNngPN8hVPkvx3ammVLA3mugnmGLl6whGcqI3MUOo',
    'YUSaImiZY8XLJ7HqEfh7lX9txuNXOWVM0jQD250RDH6eKdTbt2lDUsXhQi4JFrc8',
    'KMMGQcKEQYICtQIXSCA1GFAKzc8BVDd+deRCIPj5OPNFnvu3IyrFyJsRbpdey498',
    'nGQFUkg+xnNdtu8yCdYELA9BN3o7SKOeTcxXtvL9JatMIFB3f0CaswMkF/0uu4aS',
    '6QIDAQAB']

def test_settings_public_key():
    C1 = {**CONTENT_1_NO_SETTINGS, 'settings': [
        {'public_key': '\n'.join(PUBLIC_KEY_LINES)}
    ]}
    rr = Content(C1).export(schema='2')
    # assert len(rr['settings']['public_key'].split('\n')) == 1
    rr = Content(rr, validate=True).export(schema='1')
    assert len(rr['settings']['public_key'].split('\n')) == 7
