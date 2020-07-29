from . import flatten_survey_by_anchor
from . import xlsform_translations
from . import noop
from . import validators
from . import xlsform_aliases
from . import xlsform_choices
from . import remove_empty_rows
from . import xlsform_add_anchors

from . import fill_missing_labels

from . import kobo_rename_kuid_to_anchor
from . import koboxlsform
from . import xlsform
from . import formpack
from . import xlsform_unwrap_settings_from_list


TRANSFORMERS = {
    'validate_choices_not_list': validators.choices_not_list,
    'validate_unique_anchors': validators.unique_anchors,
    'validate_settings_not_list': validators.settings_not_list,
    'validate_has_translations': validators.has_translations,


    # convert arrays to objects with a "$start" value and "$next" values
    # to clean up diffs on small changes to large surveys
    'flatten_survey_by_anchor': flatten_survey_by_anchor,
    'anchors': flatten_survey_by_anchor,

    # convert columns like 'label::english': 'x' to 'label': ['x']
    'xlsform_translations': xlsform_translations,
    # 'formpack_prep': formpack_prep,

    'fill_missing_labels': fill_missing_labels,

    # type: 'select_one listname' split into 2
    # type: 'rank listname' split into 2
    'xlsform_aliases': xlsform_aliases,
    'xlsform_choices': xlsform_choices,
    'xlsform_add_anchors': xlsform_add_anchors,
    'xlsform_unwrap_settings_from_list': xlsform_unwrap_settings_from_list,

    'kobo_rename_kuid_to_anchor': kobo_rename_kuid_to_anchor,
    'formpack': formpack,
    'koboxlsform': koboxlsform,
    'xlsform': xlsform,
    'remove_empty_rows': remove_empty_rows,
    'noop': noop,
    '': noop,
}


ALIASES = {
    'xlsform': '1+xlsform',
    'koboxlsform': '1+koboxlsform',
}
