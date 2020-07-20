from .build_schema import MAIN_JSONSCHEMA

_translatable_refs = [
    '#/$defs/translatableMedia',
    '#/$defs/translatable',
]

def _get_translatable_props(defname):
    for (prop, vals) in MAIN_JSONSCHEMA['$defs'][defname]['properties'].items():
        if vals.get('$ref', '') in _translatable_refs:
            yield prop

def _props_for(defname):
    return MAIN_JSONSCHEMA['$defs'][defname]['properties']

def _props_set_for(defname):
    # returns a tuple (immutable)
    return tuple(set(_props_for(defname).keys()))

TRANSLATABLE_SURVEY_COLS = list(_get_translatable_props('surveyRow'))
TRANSLATABLE_CHOICES_COLS = list(_get_translatable_props('choice'))

ROW_PROPERTIES = _props_set_for('surveyRow')
CHOICE_PROPERTIES = _props_set_for('choice')
SETTINGS_PROPERTIES = _props_set_for('settings')
META_PROPERTIES = _props_set_for('metas')

GROUPABLE_TYPES = _props_for('grouping')['type']['enum']

SURVEY_ROW = MAIN_JSONSCHEMA['$defs']['surveyRow']
ROW_TYPES = MAIN_JSONSCHEMA['$defs']['surveyRowType']['enum']
SELECT_X_TYPES = set(filter(lambda _t: _t.startswith('select_'), ROW_TYPES))
