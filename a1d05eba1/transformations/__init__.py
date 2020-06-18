from . import flatten_survey_by_anchor
from . import flattened_translations
from . import noop

TRANSFORMERS = {
    # convert arrays to objects with a "$start" value and "$next" values
    # to clean up diffs on small changes to large surveys
    'flatten_survey_by_anchor': flatten_survey_by_anchor,
    'anchors': flatten_survey_by_anchor,

    # convert columns like 'label::english': 'x' to 'label': ['x']
    'flattened_translations': flattened_translations,

    'noop': noop,
    '': noop,
}
