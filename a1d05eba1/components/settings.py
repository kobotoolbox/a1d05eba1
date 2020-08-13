from ..utils.kfrozendict import kfrozendict
from ..utils import kassertfrozen
from ..utils.kfrozendict import shallowfreeze
from ..utils.yparse import yload_file
from ..schema_properties import SETTINGS_PROPERTIES

from .base_component import SurveyComponentWithDict

_standardize_public_key = lambda pk: ''.join(pk.split('\n'))


class Settings(SurveyComponentWithDict):
    _pubkey = None
    settings_renames_from_1 = yload_file('renames/from1/settings', invert=True)

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

        self._d = shallowfreeze(save)

    @kassertfrozen
    def to_frozen_dict(self, export_configs):
        out = self._d
        if self._pubkey:
            out = out.copy(public_key=self._pubkey)
        if export_configs.schema == '1' and self.content.initial_tx:
            txname = self.content.initial_tx.as_string_or_null()
            out = out.copy(default_language=txname)
        if export_configs.default_settings:
            out = out.copy(**export_configs.default_settings)
        return out
