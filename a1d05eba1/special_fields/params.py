'''
parameters string will be loaded and stored as a dictionary.

Interpret this string:

start=0 end=17 step=1

as this value:

"params": {
  "start": "0",
  "end": "17",
  "step": 1
}
'''


class Params:
    ROW_KEYS = {
        '1': ['parameters'],
        '2': ['params'],
    }
    EXPORT_KEY = 'params'


    @classmethod
    def in_row(kls, row, schema):
        if schema == '1':
            return 'parameters' in row
        elif schema == '2':
            return 'params' in row

    @classmethod
    def pull_from_row(kls, row, content):
        schema = content.schema_version
        if schema == '2':
            rowparams = row.get('params')
            if not rowparams:
                return
            yield Params(content=content, val=rowparams)
        elif schema == '1':
            val = _parse_parameters_string(row['parameters'])
            yield Params(content=content, val=val)

    def __init__(self, content, val):
        self.content = content
        self.key = 'params'
        self.val = val

    def dict_key_vals_old(self, renames=None):
        yield ('parameters', _params_to_string(self.val))

    def dict_key_vals_new(self, renames=None):
        params = self.val
        return ('params', params)


def _parse_parameters_string(parameters_string):
    '''
    converts string like this:
    > start=0 end=15 step=5

    into object like this:
    > {'start':0, 'end':15, 'step':5}
    '''
    out = {}
    for section in parameters_string.split(' '):
        (key, val) = section.split('=')
        out[key] = val
    return out

def _params_to_string(params):
    '''
    does the opposite of _parse_parameters_string(...)
    '''
    out = []
    for key, val in params.items():
        out.append(
            '{}={}'.format(key, val)
        )
    return ' '.join(out)
