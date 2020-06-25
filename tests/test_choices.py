from a1d05eba1.content import Content
from a1d05eba1.utils.kfrozendict import kfrozendict

from .common_utils import buncha_times

from copy import deepcopy
from pprint import pprint

import json


CONTENT_1 = {
    'schema': '1',
    'survey': [
        {'type': 'select_one',
          'label': ['Select state'],
          'select_from_list_name': 'states',
          'name': 'state',
          },
        {'type': 'select_one',
          'label': ['Select county'],
          'select_from_list_name': 'counties',
          'name': 'county',
          'choice_filter': 'state=${state}',
          },
      ],
    'choices': [
        {'list_name': 'states', 'value': 'CA', 'label': ['California']},
        {'list_name': 'states', 'value': 'MD', 'label': ['Maryland']},
        {'list_name': 'counties',
            'value': 'sf',
            'state': 'CA',
            'label': ['San Francisco']
            },
        {'list_name': 'counties',
            'value': 'baltimore',
            'state': 'MD',
            'label': ['Baltimore']
            },
    ],
    'translated': ['label'],
    'translations': ['English'],
}


CONTENT_2 = {'schema': '2',
    'survey': [
            {
                'label': {'tx0': 'Select state'},
                '$anchor': '$STATE',
                'name': 'state',
                'select_from': 'states',
                'type': 'select_one',
                },
            {
             'label': {'tx0': 'Select county'},
             'name': 'county',
             '$anchor': '$COUNTY',
             'select_from': 'counties',
             'choice_filter': {
                'raw': 'state=${state}'
             },
             'type': 'select_one'}],
    'choices': {
        'counties': [
            {
             'filters': {'state': 'CA'},
             'label': {'tx0': 'San Francisco County'},
             'value': 'sf',
            },
            {
             'filters': {'state': 'MD'},
             'label': {'tx0': 'Baltimore County'},
             'value': 'baltimore_cty',
            },
        ],
        'states': [
            {
             'label': {'tx0': 'California'},
             'value': 'CA',
            },
            {
             'label': {'tx0': 'Maryland'},
             'value': 'MD',
            }
        ]
    },
    'translations': [{'$anchor': 'tx0', 'default': True, 'name': 'English'}]
 }


def test_one2two():
    result = Content(CONTENT_1, perform_validation=True).export(schema='2')
    cxs = result.get('choices')
    states = cxs.get('states')
    (st0, st1) = states
    counties = result.get('choices').get('counties')
    (county0, county1) = counties
    assert 'state' not in county0
    assert 'filters' in county0


def test_buncha_times():
    '''
    aggressively go back and forth between schema:2 and schema:1
    and export to 'content'
    '''
    contents = []
    params = {
        'each': [CONTENT_1, CONTENT_2],
        'perform_validation': True,
    }
    for (content, ctx) in buncha_times(**params):
        contents.append(content)
        assert 'choice_filter' in content['survey'][1]
        choice_filter = content['survey'][1].get('choice_filter')
        if ctx.schema == '1':
            choices = content.get('choices')
            county_choices = [ii for ii in choices if ii['list_name'] == 'counties']
            for choice in county_choices:
                assert 'state' in choice
            assert isinstance(choice_filter, str)
        else:
            choices = content.get('choices')
            county_choices = choices.get('counties')
            for choice in county_choices:
                assert 'filters' in choice
                filters = choice['filters']
                assert 'state' in filters
            assert isinstance(choice_filter, dict)
    # import random
    # pprint(random.choice(contents))
