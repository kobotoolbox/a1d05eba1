from .choice_filter import ChoiceFilter
from .relevant import RelevantVal
from .constraint import ConstraintVal
from .params import Params
from .type_field import TypeField

from .tags import TagsField

ROW_SPECIAL_FIELDS = (
    ConstraintVal,
    RelevantVal,
    ChoiceFilter,
    Params,
    TagsField,
)

SPECIAL_KEYS = {
    '1': [],
    '2': [],
}

for FIELD in ROW_SPECIAL_FIELDS:
    for (schema_num, keys) in FIELD.ROW_KEYS.items():
        SPECIAL_KEYS[schema_num] = SPECIAL_KEYS[schema_num] + keys
