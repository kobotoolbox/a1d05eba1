from ..utils.kfrozendict import kfrozendict
from ..utils.yparse import yload_file

from ..fields import TranslatedVal, UntranslatedVal

# ROW_SPECIAL_FIELDS includes ChoiceFilter, RelevantVal, and ConstraintVal
from ..special_fields import (
    ConstraintVal,
    ROW_SPECIAL_FIELDS,
    SPECIAL_KEYS,
)



from .base_component import SurveyComponentWithTuple
from .base_component import SurveyComponentWithDict
from .base_component import SurveyComponentWithOrderedDict

from ..build_schema import MAIN_SCHEMA

V2_PROPERTIES = set(MAIN_SCHEMA['$defs']['surveyRow']['properties'].keys())

ALL_KOBO_TYPES = ['today',
                  'audit',
                  'barcode',
                  'audio',
                  'begin_repeat',
                  'end_repeat',
                  'image',
                  'acknowledge',
                  'username',
                  'simserial',
                  'subscriberid',
                  'deviceid',
                  'phonenumber',
                  'start',
                  'end',
                  'begin_group',
                  'end_group',
                  'begin_kobomatrix',
                  'begin_score',
                  'begin_rank',
                  'end_rank',
                  'rank__level',
                  'score__row',
                  'end_score',
                  'calculate',
                  'date',
                  'datetime',
                  'decimal',
                  'end',
                  'end_kobomatrix',
                  'file',
                  'filterType',
                  'geopoint',
                  'geoshape',
                  'geotrace',
                  'image',
                  'int',
                  'integer',
                  'note',
                  'osm',
                  'osm_buildingtags',
                  'range',
                  'select_multiple',
                  'select_multiple_from_file',
                  'select_one',
                  'select_one_external',
                  'select_one_from_file',
                  'start',
                  'string',
                  'text',
                  'time',
                  'xml-external']


class Row(SurveyComponentWithOrderedDict):
    renames_to_v1 = yload_file('renames/to1/column')
    renames_from_v1 = yload_file('renames/from1/column', invert=True)

    def load_from_2(self, **kwargs):
        _r = kfrozendict(kwargs.get('row'))
        _additionals = {}

        skip_keys = SPECIAL_KEYS['2']

        for (key, val) in _r.items():
            if key in skip_keys:
                continue
            if key not in V2_PROPERTIES:
                _additionals[key] = val
                continue

            if self.content.value_has_tx_keys(val):
                self.set_translated(key, val)
            else:
                self.set_untranslated(key, val)

        for Field in ROW_SPECIAL_FIELDS:
            if not Field.in_row(_r, schema=self.content.schema):
                continue

            for sfield in Field.pull_from_row(_r, self.content):
                self.set(Field.EXPORT_KEY, sfield)

        self._additionals = kfrozendict.freeze(_additionals)

    def append(self, val):
        key = val.key
        self.set(key, val)

    def load_from_1(self, **kwargs):
        srow = kfrozendict.freeze(kwargs.get('row'))


        skip_keys = SPECIAL_KEYS['1']

        _additionals = {}

        for (key, val) in srow.items():
            if key in skip_keys:
                continue
            original = key
            if self.content.perform_renames and key in self.renames_from_v1:
                newkey = self.renames_from_v1[key]
                if key in self.content._translated_columns:
                    self.content._translated_columns = (
                        newkey,
                    ) + self.content._translated_columns
                key = newkey

            # remove columns that are not recognized in the schema
            # (note: this may be aggressive)
            if key not in V2_PROPERTIES:
                _additionals[key] = val
                continue

            if original in self.content._translated_columns:
                col = TranslatedVal(self.content, key, val, original=original)
            else:
                col = UntranslatedVal(self.content, key, val, original=original)
            self.set(col.key, col)
        self._additionals = kfrozendict.freeze(_additionals)

        for Field in ROW_SPECIAL_FIELDS:
            if not Field.in_row(srow, schema=self.content.schema):
                continue

            for sfield in Field.pull_from_row(srow, self.content):
                self.set(Field.EXPORT_KEY, sfield)

    def to_export(self, schema='2'):
        out = []
        for colval in self:
            if schema == '2':
                out.append(colval.dict_key_vals_new())
            elif schema == '1':
                for kvs in colval.dict_key_vals_old(renames=self.renames_to_v1):
                    out.append(kvs)
        return dict(out)

    def get_row_tx_col_names_for_v1(self):
        cols = []
        for col in self:
            if isinstance(col, TranslatedVal):
                key = col.key
                if key in self.renames_to_v1:
                    key = self.renames_to_v1.get(key)
                cols.append(key)
            elif isinstance(col, ConstraintVal):
                if col.msg_txd:
                    cols.append(col.msg_txd.key)
        return cols
