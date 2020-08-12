from ..utils.kfrozendict import kfrozendict
from ..utils.kfrozendict import deepfreeze
from ..utils.yparse import yload_file
from ..schema_properties import SETTINGS_PROPERTIES

from .base_component import SurveyComponentWithDict


_standardize_public_key = lambda pk: ''.join(pk.split('\n'))

def _split_pubkey_to_64char_lines(pubkey, chars=64):
    out = ''
    while len(pubkey) > chars:
        line = pubkey[0:chars]
        pubkey = pubkey[chars:]
        out += line + '\n'
    return out + pubkey


class Settings(SurveyComponentWithDict):
    _pubkey = None
    settings_renames_from_1 = yload_file('renames/from1/settings', invert=True)
    settings_renames_to_1 = yload_file('renames/to1/settings')

    def load(self):
        SKIP_SETTINGS = ['metas', 'default_language']
        save = {}
        for (key, val) in self.content._data_settings.items():
            if key in SKIP_SETTINGS:
                continue

            if self.content.perform_renames:
                key = self.settings_renames_from_1.get(key, key)

            if key == 'style' and isinstance(val, str):
                if val == '':
                    continue
                val = val.split(' ')

            keep_setting = True
            strip_uk_setts = self.content.strip_unknown_values
            if strip_uk_setts and key not in SETTINGS_PROPERTIES:
                keep_setting = False

            if keep_setting:
                save[key] = val

        self._pubkey = save.pop('public_key', None)
        if self._pubkey:
            self._pubkey = _standardize_public_key(self._pubkey)

        self._d = deepfreeze(save)

    def to_dict_schema_1(self):
        out = []
        if self._pubkey:
            out.append(
                ('public_key', _split_pubkey_to_64char_lines(self._pubkey))
            )
        if self.content.initial_tx:
            txname = self.content.initial_tx.as_string_or_null()
            out.append(
                # initial_tx is default_language? depends on version of pyxform
                ('default_language', txname)
            )
        for (key, val) in self._d.items():
            if key in self.settings_renames_to_1:
                key = self.settings_renames_to_1[key]
            if key == 'style':
                val = ' '.join(val)
            out.append(
                (key, val)
            )
        return dict(out)

    def to_dict(self):
        out = self._d
        if self._pubkey:
            out = out.copy(public_key=self._pubkey)
        return out.unfreeze()
