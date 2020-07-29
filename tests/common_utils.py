from copy import deepcopy
from types import SimpleNamespace

from a1d05eba1.content import Content


def buncha_times(each, **kw):
    '''
    Content needs to be able to export back and forth between different schema
    values so if content matches on each iteration then thats an indication that
    it exports and reimports correctly
    '''
    for content in each:
        context = {}
        schema_patterns = [
            '1,2,1,2',
            '2,1,2,1',
            '1,2,1,1',
            '2,1,2,2',
            '1,1,2,2',
            '2,2,1,1',
        ]
        for spattern in schema_patterns:
            schemae = spattern.split(',')
            for (cnt, ctx) in _iter_load_content(content, schemae, context, **kw):
                yield (cnt, SimpleNamespace(**ctx))

def _iter_load_content(content, schemas, context, validate=True):
    # (cc, schema_str_comma) = params
    #     schema_strs = schema_str_comma.split(',')
    context = {'done':[]}
    while len(schemas) > 0:
        next_s = schemas.pop(0)
        obj = Content(content, validate=validate)
        context['object'] = obj
        context['done'].append(next_s)
        context['previously_imported_content'] = deepcopy(content)
        context['schema'] = next_s
        content = obj.export(schema=next_s)
        yield (content, context)
