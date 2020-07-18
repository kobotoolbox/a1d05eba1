from collections import defaultdict

from ..utils.kfrozendict import kfrozendict
from ..utils.yparse import yload_file

from ..fields import UntranslatedVal, TranslatedVal

from ..schema_properties import CHOICE_PROPERTIES, TRANSLATABLE_CHOICES_COLS

from .base_component import SurveyComponentWithDict
from .base_component import SurveyComponentWithOrderedDict


class Choice(SurveyComponentWithOrderedDict):
    def load(self, item, **kwargs):
        if self.content.schema == '1':
            self.load_from_old_arr(item, **kwargs)
        elif self.content.schema == '2':
            self.load_from_new_dict(item, **kwargs)

    choice_renames_to_v1 = yload_file('renames/to1/choice-column')

    renames_from_v1 = yload_file('renames/from1/column',
                                 invert=True)
    choice_specific_renames_from_v1 = yload_file('renames/from1/choice-column',
                                                 invert=True)

    def load_from_old_arr(self, item, list_name):
        self.list_name = list_name
        _additionals = {}
        for (key, val) in item.items():
            original = False
            if key in self.choice_specific_renames_from_v1:
                original = key
                key = self.choice_specific_renames_from_v1[key]
            elif key in self.renames_from_v1:
                original = key
                key = self.renames_from_v1[key]
            if key not in CHOICE_PROPERTIES:
                _additionals[key] = val
                continue
            if key in TRANSLATABLE_CHOICES_COLS:
                self.set_translated(key, val, original=original)
            else:
                self.set_untranslated(key, val, original=original)
            self.content.add_col(key, 'choices')
        self._additionals = kfrozendict.freeze(_additionals)

    def load_from_new_dict(self, item, list_name):
        self.list_name = list_name
        _filters = False
        for (key, val) in item.items():
            if key == 'filters':
                _filters = val

            if self.content.strip_unknown and key not in CHOICE_PROPERTIES:
                continue

            if key in TRANSLATABLE_CHOICES_COLS:
                self.set_translated(key, val)
            else:
                self.set_untranslated(key, val)
            self.content.add_col(key, 'choices')

        if _filters:
            self._additionals = _filters

    def to_dict(self):
        out = []
        for val in self:
            out.append(val.dict_key_vals_new())
        if len(self._additionals) > 0:
            out.append(
                ('filters', self._additionals),
            )
        return dict(out)

    def to_old_dict(self, list_name=None):
        dict_out = []
        if list_name is not None:
            dict_out.append(
                ('list_name', list_name),
            )
        if len(self._additionals) > 0:
            for (key, val) in self._additionals.items():
                dict_out.append(
                    (key, val)
                )
        for val in self:
            for (okey, oval) in val.dict_key_vals_old():
                if okey in self.choice_renames_to_v1:
                    # kpi autoname still requires choice[n].name to be used
                    okey = self.choice_renames_to_v1[okey]
                dict_out.append(
                    (okey, oval,)
                )
        return dict(dict_out)


class ChoiceLists(SurveyComponentWithDict):
    def preload(self):
        self._d = {}

    def postload(self):
        self._d = kfrozendict.freeze(self._d)

    def _append_choice_to_list(self, list_name, choice):
        cur = self._d.get(list_name, tuple())
        cur = cur + (choice,)
        self._d[list_name] = cur

    def load(self):
        self.source = self.content.data.get('choices', {})
        for (list_name, choices) in self.source.items():
            for choice in choices:
                self._append_choice_to_list(list_name,
                    Choice(content=self.content,
                           item=choice,
                           list_name=list_name)
                    )

    def to_old_arr(self):
        out = []
        for (key, vals) in self._d.items():
            for val in vals:
                out.append(val.to_old_dict(list_name=key))
        return out

    def to_dict(self, schema):
        out = {}
        for (key, vals) in self._d.items():
            out[key] = []
            for val in vals:
                out[key].append(
                    val.to_dict()
                )
        return out
