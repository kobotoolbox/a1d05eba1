from copy import deepcopy

from a1d05eba1.content_variations import build_content

simple_group = {
    'survey': [
        {'type': 'group', '$anchor': 'grp',
            'rows': [{'type': 'text', '$anchor': 'rr1'},
                     {'type': 'note', '$anchor': 'rr2'},
        ]}
    ],
    'settings': {},
}


def test_normal():
    cc = build_content(deepcopy(simple_group))
    rr = cc.export_to('1', flat=True)
    assert rr['survey'][0]['type'] == 'begin_group'
    assert rr['survey'][1]['type'] == 'text'
    assert rr['survey'][2]['type'] == 'note'
    assert rr['survey'][3]['type'] == 'end_group'

def test_ignored_text_row():
    c2 = deepcopy(simple_group)
    c2['survey'][0]['rows'][0]['type'] = '#text'
    cc = build_content(c2)
    rr = cc.export_to('1', flat=True)
    assert rr['survey'][0]['type'] == 'begin_group'
    # note, row with "#text" has been removed from flat export
    assert rr['survey'][1]['type'] == 'note'
    assert rr['survey'][2]['type'] == 'end_group'

    # but it remains in the non flat export
    rr = cc.export_to('2')
    assert rr['survey'][0]['type'] == 'group'
    assert rr['survey'][0]['rows'][0]['type'] == '#text'

def test_ignored_group():
    # should it skip exports of the rows inside the group too? ...probably
    # but since this is just trying to allow migrating forms with the
    # undocumented "disabled" column of the XLSForm i'll keep it as-is for now.
    c3 = deepcopy(simple_group)
    c3['survey'][0]['type'] = '#group'
    cc = build_content(deepcopy(c3))
    rr = cc.export_to('1', flat=True)
    assert rr['survey'][0]['type'] == 'text'
    assert rr['survey'][1]['type'] == 'note'
    assert len(rr['survey']) == 2
