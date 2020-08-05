from ..utils.kfrozendict import kfrozendict

from .flatten_survey_by_anchor import FlattenSurveyByAnchor
from .xlsform_translations import XlsformTranslations
# from . import noop
# from . import validators
from .xlsform_aliases import XlsformRenames
from .xlsform_choices import XlsformChoices
from .remove_empty_rows import RemoveEmpties

# from .xlsform_add_anchors import EnsureAnchors
# from .xlsform_add_anchors import EnsureAnchorsCopyFromName
from .anchors_when_needed import DumpExtraneousAnchors

from .fill_missing_labels import FillMissingLabels

from .kobo_rename_kuid_to_anchor import RenameKuidToAnchor
from .koboxlsform import KoboXlsform
from .choices_by_list_name import ChoicesByListName

from .xlsform import Xlsform
from .formpack import Formpack
from .xlsform_unwrap_settings_from_list import UnwrapSettingsFromList

from .transformer import Transformer

class SettingsToList(Transformer):
    def fw__1(self, content):
        assert isinstance(content['settings'], kfrozendict)
        return content.copy(settings=(content['settings'],))

class ChoicesToList(Transformer):
    def fw__1(self, content):
        assert isinstance(content['choices'], kfrozendict)
        all_choices = ()
        for (list_name, choices) in content['choices'].items():
            for choice in choices:
                all_choices = all_choices + (
                    choice.copy(list_name=list_name),
                )
        return content.copy(choices=all_choices)

class ChoicesFromList(Transformer):
    def rw(self, content):
        if 'choices' in content and isinstance(content['choices'], (dict, kfrozendict)):
            return content
        _choice_lists = {}
        for choice in content['choices']:
            (list_name, choice) = choice.popout('list_name')
            _list = _choice_lists.get(list_name, ())
            _list = _list + (
                choice,
            )
            _choice_lists[list_name] = _list
        return content.copy_in(choices=_choice_lists)

class Autoname(Transformer):
    def rw__each_row(self, row):
        if 'name' not in row and '$autoname' in row:
            return row.copy(name=row.get('$autoname'))
        # /end_group's don't have names, e.g.
        return row

TRANSFORMERS = {
    'flatten_survey_by_anchor': FlattenSurveyByAnchor,
    'anchors': FlattenSurveyByAnchor,
    'xlsform_translations': XlsformTranslations,
    'fill_missing_labels': FillMissingLabels,
    'xlsform_aliases': XlsformRenames,
    'xlsform_choices': XlsformChoices,
    'autoname': Autoname,
    # 'xlsform_add_anchors': EnsureAnchors,
    'xlsform_unwrap_settings_from_list': UnwrapSettingsFromList,
    'choices_by_list_name': ChoicesByListName,
    'choices_by_list_name': ChoicesByListName,
    'kobo_rename_kuid_to_anchor': RenameKuidToAnchor,
    'choices_frm_list': ChoicesFromList,
    'formpack': Formpack,
    'koboxlsform': KoboXlsform,
    'xlsform': Xlsform,
    'remove_empty_rows': RemoveEmpties,
    'settings_2_list': SettingsToList,
    'choices_2_list': ChoicesToList,
    'remove_extraneous_anchors': DumpExtraneousAnchors,
}


ALIASES = {
    'xlsform': '1+xlsform',
    'koboxlsform': '1+koboxlsform',
}
