from .choice_filter import ChoiceFilter
from .relevant import RelevantVal
from .constraint import ConstraintVal
from .params import Params

ROW_SPECIAL_FIELDS = (
    ConstraintVal,
    RelevantVal,
    ChoiceFilter,
    Params,
)

SPECIAL_KEYS = {
    '1': [],
    '2': [],
}

for FIELD in ROW_SPECIAL_FIELDS:
    for (schema_num, keys) in FIELD.ROW_KEYS.items():
        SPECIAL_KEYS[schema_num] = SPECIAL_KEYS[schema_num] + keys

class TypeField:
    def __init__(self, content, typestring):
        self.key = 'type'
        self.val = typestring
        if typestring in ['group']:
            self.flat_val = 'begin_%s' % self.val
