import os
import re
import json
import string
import random


from .utils.kfrozendict import kfrozendict
from .utils.yparse import yparse, yload_file, invert, yload_definition

from .exceptions import SchemaError

# components
from .components import Surv
from .components import ChoiceLists, Choice
from .components import TxList, Translation
from .components import Settings
from .components import Metas

from .components.base_component import SurveyComponentWithTuple, SurveyComponentWithDict

from .transformations import TRANSFORMERS

SCHEMAS = [
    '1',
    '2',
]

SCHEMA_ALIASES = {
    '1+::': '1+flattened_translations',
    '1::': '1+flattened_translations',
    'xlsform': '1+flattened_translations',
}
SCHEMA_ALIASES_REVERSE = dict([(v, k) for (k, v) in SCHEMA_ALIASES.items()])

def unpack_schema_string(schema):
    schema = SCHEMA_ALIASES.get(schema, schema)
    [schema, *transformations] = [ss.strip()
                                  for ss in re.split(r'\++', schema)]
    return (schema, transformations)




METAS = yload_file('defs/_settingsMetas')

DEPTH = 0


def _unpack_v1_settings(_dsetts=None):
    # pulls first item from an array, defaults to an empty object
    if _dsetts is None:
        return {}
    if isinstance(_dsetts, (list, tuple)):
        if len(_dsetts) > 0:
            return _unpack_v1_settings(_dsetts[0])
        else:
            return {}
    return _dsetts


def _sans_empty_values(obj):
    # remove keys with 'None' as a value in the returned dict
    for delete_key in [k for (k, v) in obj.items() if v is None]:
        del obj[delete_key]
    return obj


class Content:
    # is this the right place for these properties? 🤔
    META_TYPES = set(METAS['properties'].keys())
    ANCHOR_KEY = '$anchor'

    def __init__(self,
                 content,
                 perform_validation=False,
                 generate_anchors=False,
                 anchor_generator=False,
                 exports_include_defaults=False,
                 strip_unknown=False,
                 ):
        content = kfrozendict.freeze(content)
        self._translated_columns = None
        self.perform_renames = True
        self.perform_transformations = True

        self.generate_anchors = generate_anchors
        if anchor_generator:
            self.anchor_generator = anchor_generator

        self.remove_nulls = not exports_include_defaults
        self.strip_unknown = strip_unknown

        self.perform_validation = perform_validation

        self.default_tx = False

        try:
            schema = content['schema']
        except KeyError as err:
            raise ValueError('content.schema not found')


        (schema, transformations) = unpack_schema_string(schema)

        if len(transformations) > 0:
            for transformation in transformations:
                content = TRANSFORMERS[transformation].rw(content)

        self._v = schema
        self.schema = self._v

        self.data = kfrozendict.freeze(content)

        if self._v == '1':
            self.load_content_schema_1()
        elif self._v == '2':
            self.load_content_schema_2()

        if self.generate_anchors:
            for row in self.survey:
                if not row.has('$anchor'):
                    _anchor = self.anchor_generator()
                    row.set_untranslated('$anchor', _anchor)
            for (cname, clist) in self.choices.items():
                for choice in clist:
                    has_anchor = False
                    for kv in choice:
                        if kv.key == '$anchor':
                            has_anchor = True
                    if not has_anchor:
                        _anchor = self.anchor_generator()
                        choice.set_untranslated('$anchor', _anchor)

        if self.perform_validation:
            self._validate_export()

    def _validate_export(self):
        validate(self.export(schema='2'), JSONSCHEMA)

    def anchor_generator(self):
        length = 9
        alphabet = string.ascii_lowercase + string.digits
        return ''.join([
            random.choice(string.ascii_lowercase),
        ] + [
            random.choice(alphabet) for _ in range(length - 1)
        ])

    def ensure_default_language(self):
        _from_setting = self._data_settings.get('default_language')
        if not self.default_tx:
            dtx_index = 0
            if _from_setting:
                names = [tx.as_string_or_null() for tx in self.txs]
                if _from_setting in names:
                    dtx_index = names.index(_from_setting)
            if len(self.txs) > 0:
                self.default_tx = self.txs._tuple[dtx_index]

    def export(self, schema='2'):
        result = None

        # completed_transformations = []
        (schema, transformations) = unpack_schema_string(schema)

        if schema == '1':
            result = self.to_v1_structure()
        else:
            result = self.to_structure(schema=schema)


        result = kfrozendict.freeze(result)
        schemas = [schema]
        for transformation in transformations:
            result = TRANSFORMERS[transformation].fw(result)
            schemas.append(transformation)
        # result = kfrozendict.unfreeze(result)

        return kfrozendict.unfreeze(
            result.copy(schema='+'.join(schemas))
        )

    def value_has_tx_keys(self, val):
        if not isinstance(val, (dict, kfrozendict)):
            return False
        valkeys = set(val.keys())
        _has_tx_keys = len(valkeys) > 0 and valkeys.issubset(self.txs.codes)
        if not _has_tx_keys and 'tx0' in valkeys:
            raise Exception('missing tx key?')
        return _has_tx_keys

    def to_structure(self, schema='2'):
        return _sans_empty_values(kfrozendict.unfreeze({
            'schema': schema,
            'translations': self.txs.to_list(schema=schema),
            'survey': self.survey.to_list(schema=schema),
            'choices': self.choices.to_dict(schema=schema),
            'settings': self.settings.to_dict(schema=schema),
        }))

    def load_content_schema_2(self):
        content = self.data
        self._data_settings = self.data.get('settings', {})

        self.metas = Metas(content=self)
        self.txs = TxList(content=self)

        self.ensure_default_language()

        _ctmp = content.get('choices', {})
        self.choices = ChoiceLists(content=self)

        self.survey = Surv(content=self)
        self.settings = Settings(content=self)


    def load_content_schema_1(self):
        content = self.data
        self._data_settings = _unpack_v1_settings(self.data.get('settings'))

        if 'choices' not in content:
            self.data = self.data.copy(choices=[])

        _tcols = self.data.get('translated', [])
        self._translated_columns = _tcols
        self.metas = Metas(content=self)
        self.txs = TxList(content=self)
        self.ensure_default_language()
        self.choices = ChoiceLists(content=self)
        self.survey = Surv(content=self)
        self.settings = Settings(content=self)

    def to_v1_structure(self):
        colnames = self.survey.get_tx_col_names_for_v1().union(
            self.choices.get_tx_col_names_for_v1()
        )
        return kfrozendict.unfreeze({
            'schema': '1',
            'translated': sorted(colnames),
            'translations': self.txs.to_v1_strings(),
            'survey': self.survey.to_list(schema='1'),
            'choices': self.choices.to_old_arr(),
            'settings': self.settings.to_dict(schema='1'),
        })
