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
XLSFORM_SETTINGS_RENAMES = yload_file('renames/to1/settings')

class XlsformRenames(Transformer):
    def fw__1__each_row(self, row):
        if 'select_from_list_name' in row:
            (row, list_name) = row.popout('select_from_list_name')
            _type = ' '.join([row.get('type'), list_name])
            return row.copy(type=_type)
        return row

    def fw__1__settings(self, settings):
        settings = fw_settings_split_pubkey(settings)
        settings = fw_settings_style(settings)
        for key in settings.keys():
            new_key = XLSFORM_SETTINGS_RENAMES.get(key)
            if new_key:
                settings = settings.renamed(key, new_key)
        return settings

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


def fw_settings_split_pubkey(settings):
    '''
    if "public_key" exists in the settings, split the public_key to match
    the format that ODK is expecting. (max line length of 64)
    '''
    pubkey_in = settings.get('public_key')
    if not pubkey_in:
        return settings
    pubkey_out = ''
    while len(pubkey_in) > 64:
        line = pubkey_in[0:64]
        pubkey_in = pubkey_in[64:]
        pubkey_out += line + '\n'
    pubkey_out = pubkey_out + pubkey_in
    return settings.copy(public_key=pubkey_out)

def fw_settings_style(settings):
    style = settings.get('style')
    if not style:
        return settings
    return settings.copy(style=' '.join(style))
