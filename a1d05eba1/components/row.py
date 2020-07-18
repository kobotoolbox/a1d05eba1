from ..utils.kfrozendict import kfrozendict
from ..utils.yparse import yload_file

from ..fields import TranslatedVal, UntranslatedVal

from ..special_fields import (
    ConstraintVal,
    ROW_SPECIAL_FIELDS, # <-- ChoiceFilter, RelevantVal, and ConstraintVal
    SPECIAL_KEYS,
    TypeField,
)

from .base_component import SurveyComponentWithOrderedDict

from ..schema_properties import ROW_PROPERTIES
from ..schema_properties import TRANSLATABLE_SURVEY_COLS

# from ..build_schema import schema_for_def
# from jsonschema import validate
# ROW_SCHEMA = schema_for_def('surveyRow')


class Parented:
    '''
    a superclass of a survey "row" that exists as a child of either the survey
    or a group within the survey.
    '''
    _parent = False
    is_end = False

    def set_parent(self, parent):
        self._parent = parent
        self._parent.rows = self._parent.rows + (self,)
        return self


class Row(SurveyComponentWithOrderedDict, Parented):
    ALLOWED_PROPERTIES = ROW_PROPERTIES
    renames_to_v1 = yload_file('renames/to1/column')
    renames_from_v1 = yload_file('renames/from1/column', invert=True)
    rows = tuple()
    _anchor = False

    def postload(self, **kwargs):
        assert self._anchor is not False
        assert hasattr(self, 'type')

    def load_from_2(self, **kwargs):
        (_r, anchor) = kfrozendict(kwargs.get('row')).popout('$anchor')
        self._anchor = anchor
        _additionals = {}

        skip_keys = SPECIAL_KEYS['2']

        for (key, val) in _r.items():
            if key in skip_keys:
                continue
            if key not in self.ALLOWED_PROPERTIES:
                _additionals[key] = val
                continue
            if key == 'type':
                self.typefield = TypeField(self.content, val)
                self.type = self.typefield.val
                self.set('type', self.typefield)
                continue

            # formerly-- self.content.value_has_tx_keys(val)
            if key in TRANSLATABLE_SURVEY_COLS:
                self.set_translated(key, val)
            else:
                self.set_untranslated(key, val)
            self.content.add_col(key, 'survey')

        for Field in ROW_SPECIAL_FIELDS:
            if not Field.in_row(_r, schema=self.content.schema_version):
                continue

            for sfield in Field.pull_from_row(_r, self.content):
                self.set(Field.EXPORT_KEY, sfield)

        self._additionals = kfrozendict.freeze(_additionals)

    def load_from_1(self, **kwargs):
        srow = kfrozendict.freeze(kwargs.get('row'))
        if '$kuid' in srow:
            raise ValueError('unexpected value: $kuid')
        if '$anchor' in srow:
            (srow, anchor) = srow.popout('$anchor')
            self._anchor = anchor

        if self._anchor in (None, False):
            raise ValueError('No "$anchor" value found for row')

        skip_keys = SPECIAL_KEYS['1']

        _additionals = {}

        for (key, val) in srow.items():
            if key in skip_keys:
                continue
            original = key
            if self.content.perform_renames and key in self.renames_from_v1:
                newkey = self.renames_from_v1[key]
                key = newkey

            # remove columns that are not recognized in the schema
            # (note: this may be aggressive)
            if key not in self.ALLOWED_PROPERTIES:
                _additionals[key] = val
                continue

            if key == 'type':
                self.type = val
                self.typefield = TypeField(self.content, val)
                col = self.typefield
            elif original in self.content._tx_columns:
                col = TranslatedVal(self.content, key, val, original=original)
            elif key in TRANSLATABLE_SURVEY_COLS:
                # same as previous condition, but when a column *should* be txd
                # but was not marked as translatable
                col = TranslatedVal(self.content, key, val, original=original)
            else:
                col = UntranslatedVal(self.content, key, val, original=original)

            self.set(col.key, col)
        self._additionals = kfrozendict.freeze(_additionals)

        for Field in ROW_SPECIAL_FIELDS:
            if not Field.in_row(srow, schema=self.content.schema_version):
                continue

            for sfield in Field.pull_from_row(srow, self.content):
                self.set(Field.EXPORT_KEY, sfield)

    @property
    def non_type_fields(self):
        for (item) in self._values:
            if not isinstance(item, TypeField):
                yield item

    def flat_export(self, schema='2'):
        type_val = self.typefield.val
        if hasattr(self.typefield, 'flat_val'):
            type_val = self.typefield.flat_val
        anchor_key = '$anchor'
        out = [
            ('type', type_val),
            (anchor_key, self._anchor),
        ]
        for colval in self.non_type_fields:
            if schema == '2':
                out.append(colval.dict_key_vals_new())
            elif schema == '1':
                for kvs in colval.dict_key_vals_old(renames=self.renames_to_v1):
                    out.append(kvs)
        outbound = dict(out)
        # validate(outbound, ROW_SCHEMA)
        return outbound

    def nested_export(self, schema='2'):
        if not self.is_end:
            out = [
                ('type', self.typefield.val),
                ('$anchor', self._anchor),
            ]
            for colval in self.non_type_fields:
                out.append(colval.dict_key_vals_new())
            if len(self.rows) > 0:
                subrows = []
                for sbrow in self.rows:
                    for deets in sbrow.nested_export(schema=schema):
                        subrows.append(deets)
                out.append(
                    ('rows', subrows)
                )
            yield dict(out)

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


class OpeningRow(Row):
    ALLOWED_PROPERTIES = ROW_PROPERTIES + ('repeat_count',)

    def adjust_kwargs(self, kwargs):
        row = kwargs['row']
        if row['type'].startswith('begin_'):
            row = row.copy(type=row['type'].replace('begin_', ''))
            kwargs['row'] = row
        return kwargs


class ClosingRow(Parented):
    '''
    ClosingRow is only exported on "flat" exports
    '''
    is_end = True

    def nested_export(self, **kwargs):
        if kwargs.get('include_group_ends'):
            yield self

    def flat_export(self, schema='2'):
        return {'type': self.type, '$anchor': self.compiled_anchor()}

    @property
    def type(self):
        return 'end_' + self._parent.type

    def has(self, key):
        return key in [ANCHOR_KEY, 'type']

    def compiled_anchor(self):
        return '/' + self._parent._anchor

    def get_row_tx_col_names_for_v1(self):
        return []
