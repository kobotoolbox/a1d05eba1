from .transformer import Transformer
from ..schema_properties import SURVEY_ROW

NOT_FALSEY_SURVEY_FIELDS = []
for (prop, vals) in SURVEY_ROW['properties'].items():
    for _item in vals.get('allOf', []):
        if _item.get('$ref', '') == '#/$defs/notFalseyBooleanString':
            NOT_FALSEY_SURVEY_FIELDS.append(prop)

FALSEY_VALS = ['false',
               'false()',
               'no']

TRUTHY_VALS = ['true',
               'true()',
               'yes']


class ReplaceTruthyStrings(Transformer):
    '''
    TRUTHY_VALS and FALSEY_VALS will be compared to
    val.lower() values from survey[n]['required'],
    for example

    This Transformer replaces string values like
        "yes" "true" / "no" "false"
    with their boolean representation.

    It acts on fields in NOT_FALSEY_SURVEY_FIELDS
    such as "required".
    '''
    def fw__each_row(self, row):
        if 'required' in row:
            req = row['required']
            req_str = 'true()' if req else 'false()'
            return row.copy(required=req_str)
        return row

    def rw__each_row(self, row):
        for key in NOT_FALSEY_SURVEY_FIELDS:
            if key in row:
                val = row[key]
                if not isinstance(val, str):
                    continue
                val = val.lower()
                if val in FALSEY_VALS:
                    return row.copy(**{key: False})
                if val in TRUTHY_VALS:
                    return row.copy(**{key: True})
        return row

TRANSFORMER = ReplaceTruthyStrings()
