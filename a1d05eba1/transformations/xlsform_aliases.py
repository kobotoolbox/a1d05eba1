'''
xlsform_aliases:

iterate through the survey, choices, and settings sheets to replace known
aliases with their proper value.

aliases are pulled from 'yml/renames/from1'
'''

from ..utils.yparse import yload_file
from ..schema_properties import SELECT_X_TYPES
from .transformer import Transformer

XLSFORM_RENAMES = yload_file('renames/from1/xlsformTypes', invert=True)


class XlsformRenames(Transformer):
    def fw__each_row(self, row):
        if 'select_from_list_name' in row:
            (row, list_name) = row.popout('select_from_list_name')
            _type = ' '.join([row.get('type'), list_name])
            return row.copy(type=_type)
        return row

    def rw__each_row(self, row):
        _type = row['type']
        if _type in XLSFORM_RENAMES:
            _type = XLSFORM_RENAMES[_type]
            return row.copy(type=_type)
        for s_alias in SELECT_X_TYPES:
            s_alias_spaced = '{} '.format(s_alias)
            if s_alias_spaced in _type:
                changes = {'type': s_alias.strip(),
                    'select_from_list_name': _type.replace(s_alias, '').strip(),
                }
                return row.copy(**changes)
        return row.copy(type=_type)
