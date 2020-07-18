'''
xlsform_aliases:

iterate through the survey, choices, and settings sheets to replace known
aliases with their proper value.

aliases are pulled from 'yml/renames/from1'
'''

from ..utils.yparse import yload_file
from ..schema_properties import SELECT_X_TYPES

XLSFORM_RENAMES = yload_file('renames/from1/xlsformTypes', invert=True)


def fw(content):
    survey = tuple()
    for row in content.get('survey', []):
        survey = survey + (fw__each_row(row),)
    return content.copy(survey=survey)

def fw__each_row(row):
    if 'select_from_list_name' in row:
        (row, list_name) = row.popout('select_from_list_name')
        _type = ' '.join([row.get('type'), list_name])
        return row.copy(type=_type)
    return row


def rw(content):
    survey = tuple()
    for row in content.get('survey', []):
        survey = survey + (rw__each_row(row),)
    return content.copy(survey=survey)

def rw__each_row(row):
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
