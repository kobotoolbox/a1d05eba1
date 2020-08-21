from a1d05eba1.content_variations import build_content
from a1d05eba1.content_variations import V2_Content
from a1d05eba1.export_configs import (
    ExportConfigs,
    DefaultExportConfigs,
    DefaultExportConfigsSchema1,
)

CONTENT = {
    'survey': [
        {'type': 'text', '$anchor': 'abcabc', 'name': 'q1',
         'label': {'tx0': 'la belle'}},
    ],
    'translations': [{'$anchor': 'tx0', 'name': ''}],
    'settings': {'identifier': 'example'},
}


def test_export_simp():
    cc = V2_Content(CONTENT)
    result = cc.export_to('1')
    assert result['survey'][0]['label'] == ['la belle']

    result = cc.export_to('2')
    assert result['survey'][0]['label'] == {'tx0': 'la belle'}

def test_export_to_configs():
    cc = V2_Content(CONTENT)
    result = cc.export_to(DefaultExportConfigsSchema1)
    assert result['survey'][0]['label'] == ['la belle']

    result = cc.export_to(DefaultExportConfigs)
    assert result['survey'][0]['label'] == {'tx0': 'la belle'}
