from a1d05eba1.content import Content

from .common_utils import buncha_times

BASIC_1 = {
    'schema': '1',
    'translations': [None],
    'settings': {},
}

BASIC_2 = {
    'schema': '2',
    'translations': [{'name':'', '$anchor': 'xx'}],
    'settings': {},
}


def test_parameters():
    '''
    tests a barebones survey content in schema 1 and schema 2 with
    the simplest value for the 'parameters'/'params' field
    '''
    basic = {**BASIC_1, 'survey': [
            {'type': 'text',
                'parameters': 'start=0 end=15 step=1'}
        ]}

    basic_2 = {**BASIC_2, 'survey': [
            {'type': 'text',
                # '$anchor': 'xx',
                'params': {'start': '0', 'end': '15', 'step': '5'}}
        ]}

    kwargs = {
        'each': [basic, basic_2],
        'perform_validation': True,
    }

    for (content, ctx) in buncha_times(**kwargs):
        row0 = content['survey'][0]
        if ctx.schema == '1':
            assert 'parameters' in row0
        elif ctx.schema == '2':
            assert 'params' in row0
