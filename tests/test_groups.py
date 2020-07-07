from a1d05eba1.content import Content


def cc1():
    return Content({
        'schema': '2',
        'survey': [
            {'type': 'begin_group',
             '$anchor': 'g1'},
            {'type': 'begin_group',
             '$anchor': 'g2'},
            {'type': 'begin_group',
             '$anchor': 'g3'},
            {'type': 'text',
            '$anchor': 't1'},
            {'type': 'end_group',
             '$anchor': '/g3'},
            {'type': 'end_group',
             '$anchor': '/g2'},
            {'type': 'end_group',
             '$anchor': '/g1'},
        ]
    })

def cc9():
    return Content({
        'schema': '2',
        'survey': [
            {'type': 'group',
             '$anchor': 'g1',
             'rows': [
                {'type': 'group',
                 '$anchor': 'g2',
                 'rows': [
                    {'type': 'group',
                     '$anchor': 'g3',
                     'rows': [
                        {'type': 'text',
                        '$anchor': 't1'},
                     ],
                    },
                 ],
                },
             ],
            },
        ],
        'translations': [{'name': '', '$anchor': 'tx0'}]
    })


def test_surv_equiv_transforms():
    for cc in [cc1(), cc9()]:
        [row0, row1, row2, row3, row4, row5, row6] = list(cc.survey._tuple)
        assert row0._parent == cc.survey
        assert row1._parent == row0
        assert row2._parent == row1
        assert row3._parent == row2
        assert row4._parent == row2
        assert row5._parent == row1
        assert row6._parent == row0

        assert row4.to_flat_export() == {'$anchor': '/g3', 'type': 'end_group'}

        [row0] = cc.survey.rows
        assert row0.type == 'group'

        result = cc.export(schema='2', flat=True)
        assert len(result['survey']) == 7

        tanks = cc.export(schema='1', flat=True) # schema 1 defaults

        typs = cc._tanchors(schema='1', flat=True, key='type')
        assert typs == ['begin_group',
                        'begin_group',
                        'begin_group',
                        'text',
                        'end_group',
                        'end_group',
                        'end_group']

        zz = cc.export(schema='2', flat=False)
        assert len(cc.survey[0].rows) == 2 # g1, /g1
        assert len(cc.survey[1].rows) == 2 # g2, /g2
        assert len(cc.survey[2].rows) == 2 # g3, /g3

        tanks2 = cc._tanchors(schema='2', flat=False)
        assert tanks2 == ['g1', 'g1.g2', 'g1.g2.g3', 'g1.g2.g3.t1']

        types = cc._tanchors(schema='2', flat=False, key='type')
        assert types == ['group',
                         'group.group',
                         'group.group.group',
                         'group.group.group.text']

        types = cc._tanchors(schema='2', flat=True, key='type')
        assert types == ['begin_group',
                         'begin_group',
                         'begin_group',
                         'text',
                         'end_group',
                         'end_group',
                         'end_group']


from pprint import pprint

from a1d05eba1.build_schema import MAIN_JSONSCHEMA
from jsonschema import validate

def test_odd_group_tree():
    cc = Content({
        'schema': '2',
        'survey': [
            {'type': 'group',
             '$anchor': 'g1',
             'rows': [
                {'type': 'group',
                 '$anchor': 'g2',
                 'rows': [
                    {'type': 'text',
                    '$anchor': 'g2t1'},
                 ],
                },
                {'type': 'group',
                 '$anchor': 'g3',
                 'rows': [
                    {'type': 'text',
                    '$anchor': 'g3t1'},
                    {'type': 'integer',
                    '$anchor': 'g3t2'},
                    {'type': 'image',
                    '$anchor': 'g3t3'},
                 ],
                },
             ],
            },
        ],
        'translations': [{'name': '', '$anchor': 'tx0'}]
    })
    result = cc.export(schema='2', flat=False)
    validate(result, MAIN_JSONSCHEMA)
