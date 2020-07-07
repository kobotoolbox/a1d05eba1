from . import flatten_survey_by_anchor
from . import xlsform_translations
from . import noop
from . import xlsform_aliases
from . import remove_empty_rows
from . import kuid_anchor_key


class Transformer:
    def __init__(self, module):
        self.module = module

    def fw(self, content):
        _tcontent = self.module.fw(content)
        if _tcontent is None:
            return content
        return _tcontent

    def rw(self, content):
        _tcontent = self.module.rw(content)
        if _tcontent is None:
            return content
        return _tcontent


TRANSFORMERS = {
    # convert arrays to objects with a "$start" value and "$next" values
    # to clean up diffs on small changes to large surveys
    'flatten_survey_by_anchor': flatten_survey_by_anchor,
    'anchors': flatten_survey_by_anchor,

    # convert columns like 'label::english': 'x' to 'label': ['x']
    'xlsform_translations': xlsform_translations,

    # type: 'select_one listname' split into 2
    # type: 'rank listname' split into 2
    'xlsform_aliases': xlsform_aliases,

    'kuid_anchor_key': kuid_anchor_key,
    'remove_empty_rows': Transformer(remove_empty_rows),

    'noop': noop,
    '': noop,
}


ALIASES = {
    '1::': '1+xlsform_translations',
    '1+::': '1+xlsform_translations',
    'xlsform': '+'.join([
        '1',
        'xlsform_aliases',
        'xlsform_translations',
        'remove_empty_rows',
    ]),
    'koboxlsform': '+'.join([
        '1',
        'xlsform_aliases',
        'xlsform_translations',
        'kuid_anchor_key',
        'remove_empty_rows',
    ]),
}
