from ..utils.kfrozendict import kfrozendict
from ..utils.yparse import yload_file
from ..schema_properties import SETTINGS_PROPERTIES

from .base_component import SurveyComponentWithTuple, SurveyComponentWithDict


_standardize_public_key = lambda pk: ''.join(pk.split('\n'))

def _split_pubkey_to_64char_lines(pubkey, chars=64):
    out = ''
    while len(pubkey) > chars:
        line = pubkey[0:chars]
        pubkey = pubkey[chars:]
        out += line + '\n'
    return out + pubkey


class Settings(SurveyComponentWithDict):
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
            strip_uk_setts = self.content.strip_unknown
            if strip_uk_setts and key not in SETTINGS_PROPERTIES:
                keep_setting = False

            if keep_setting:
                save[key] = val

        self._pubkey = save.pop('public_key', None)
        if self._pubkey:
            self._pubkey = _standardize_public_key(self._pubkey)

        self._d = kfrozendict.freeze(save)

    def to_dict(self, schema):
        if schema == '2':
            out = kfrozendict.unfreeze(self._d)
            if self._pubkey:
                out['public_key'] = self._pubkey
            if len(out) == 0 and self.content.export_params.remove_nulls:
                return None
            return out
        elif schema == '1':
            out = []
            if self._pubkey:
                out.append(
                    ('public_key', _split_pubkey_to_64char_lines(self._pubkey))
                )
            if self.content.default_tx != False:
                dtxname = self.content.default_tx.as_string_or_null()
                out.append(
                    ('default_language', dtxname)
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
