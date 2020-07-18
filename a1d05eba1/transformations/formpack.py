# from . import formpack_xlsform_translations
from . import xlsform_translations
from . import xlsform_aliases
from . import remove_empty_rows
from . import xlsform_metas_to_settings
from . import xlsform_initial_renames
from . import xlsform_unwrap_settings_from_list
from . import xlsform_add_anchors
from . import xlsform_replace_truthy_strings

from . import validators

from .transformer import TransformerList

TRANSFORMER = TransformerList([
    xlsform_initial_renames,    # 'list name' becomes 'list_name'
    remove_empty_rows,          # rows without required columns get removed
    xlsform_unwrap_settings_from_list,
                                # content.settings is a dict
    # ensure proper structure:
    validators.settings_not_list,

    xlsform_metas_to_settings,
    # formpack_xlsform_translations,
    xlsform_translations,

    xlsform_aliases,
    xlsform_replace_truthy_strings,
    xlsform_add_anchors,

    # ensure unique anchors:
    validators.unique_anchors,
])
