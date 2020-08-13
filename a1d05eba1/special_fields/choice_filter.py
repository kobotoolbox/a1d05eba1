from ..utils.kfrozendict import kfrozendict
from ..utils.kfrozendict import kassertfrozen

class ChoiceFilter:
    ROW_KEYS = {
        '1': ['choice_filter'],
        '2': ['choice_filter'],
    }
    EXPORT_KEY = 'choice_filter'


    @classmethod
    def in_row(kls, row, schema):
        return 'choice_filter' in row

    @classmethod
    def pull_from_row(kls, row, content):
        schema = content.schema_version
        if schema == '2':
            cfdata = row.get('choice_filter')
            if not cfdata:
                return
            assert 'raw' in cfdata
            yield ChoiceFilter(content=content, val=cfdata)
        elif schema == '1':
            cfdata = {'raw': row['choice_filter']}
            yield ChoiceFilter(content=content, val=cfdata)

    def __init__(self, content, val):
        self.content = content
        self.key = 'choice_filter'
        self.val = val
        self._string = val.get('raw')

    def dict_key_vals_old(self, renames=None):
        # print(('choice_filter', self._string,))
        yield ('choice_filter', self._string,)

    @kassertfrozen
    def dict_key_vals_new(self, renames=None):
        return (
            'choice_filter',
            kfrozendict(raw=self.val.get('raw')),
        )
