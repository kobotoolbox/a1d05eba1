from ..utils.kfrozendict import kfrozendict

class RelevantVal:
    ROW_KEYS = {
        # by schema
        '1': ['relevant'],
        '2': ['relevant'],
    }
    EXPORT_KEY = 'relevant'

    @classmethod
    def in_row(kls, row, schema):
        return 'relevant' in row

    @classmethod
    def pull_from_row(kls, row, content):
        schema = content.schema
        if 'relevant' not in row:
            return
        else:
            yield kls(content, row['relevant'])

    def __init__(self, content, val):
        self.content = content
        self.key = 'relevant'
        if isinstance(val, str):
            self.string = val
        elif isinstance(val, (dict, kfrozendict)):
            self.string = val.get('string')
        self.val = {'string': self.string}

    def dict_key_vals_old(self, renames=None):
        yield ('relevant', self.string)

    def dict_key_vals_new(self):
        return ('relevant', self.val)