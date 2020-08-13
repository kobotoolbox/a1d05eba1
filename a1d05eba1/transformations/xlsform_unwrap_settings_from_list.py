'''
xlsform_unwrap_settings_from_list:

if settings is a list, pull out the first item.
settings is always a dict
'''

from .transformer import TransformerRW
from ..utils.kfrozendict import kfrozendict

class UnwrapSettingsFromListRW(TransformerRW):
    '''
    when loaded in from an XLSForm, settings is in a 1-item-list

    this will pull the 1st item out of the settings list and update
    the content.settings

    before:
      settings:
        [{'default_language': 'Latin'}]

    after:
      settings:
        {'default_language': 'Latin'}
    '''
    def rw__2(self, content):
        if 'settings' not in content:
            return content.copy(settings=kfrozendict())
        return content

    def rw__1(self, content):
        if 'settings' not in content:
            return content.copy(settings=kfrozendict())
        settings = content['settings']
        if isinstance(settings, (list, tuple)):
            if len(settings) > 0:
                settings = settings[0]
            else:
                settings = kfrozendict()
        return content.copy(settings=settings)
