import os
import re
import json
import string
import random

from types import SimpleNamespace

from jsonschema import validate

from .utils.kfrozendict import kfrozendict

from .exceptions import SchemaError

# components
from .components import Surv
from .components import ChoiceLists, Choice
from .components import TxList, Translation
from .components import Settings
from .components import Metas

from .components.base_component import SurveyComponentWithTuple, SurveyComponentWithDict
from .build_schema import MAIN_JSONSCHEMA

from .transformations import TRANSFORMERS
from .transformations.transformer import TransformerList
from .transformations import ALIASES as TRANSFORMER_ALIASES

from .schema_properties import TRANSLATABLE_SURVEY_COLS

FLAT_DEFAULT = True
METAS = MAIN_JSONSCHEMA['$defs']['metas']

SCHEMAS = [
    '1',
    '2',
]

def unpack_schema_string(schema):
    '''
    schema string, if in the format:
      1+something+something_else

    will unpack to the following values
      schema='1'
      transformer_names=('something', 'something_else',)

    See transformers/__init__.py for aliases.
    '''
    schema = TRANSFORMER_ALIASES.get(schema, schema)
    [schema, *transformations] = [ss.strip()
                                  for ss in re.split(r'\++', schema)]
    return (schema, transformations)


def _sans_empty_values(obj):
    # remove keys with 'None' as a value in the returned dict
    for delete_key in [k for (k, v) in obj.items() if v is None]:
        del obj[delete_key]
    return obj

DEFAULT_TRANSFORMERS = {
    '1': ['xlsform_unwrap_settings_from_list',
          'xlsform_choices',
          ]
}


class Content:
    META_TYPES = set(METAS['properties'].keys())

    @property
    def _tx_columns(self):
        txc = []
        for col in self._known_columns:
            if col in TRANSLATABLE_SURVEY_COLS:
                txc.append(col)
        return txc

    def add_col(self, colname, sheet):
        if colname not in self._known_columns:
            self._known_columns = self._known_columns + (colname,)

    def __init__(self,
                 content,
                 perform_validation=False,
                 exports_include_defaults=False,
                 strip_unknown=False,
                 ):

        self._known_columns = tuple()

        if content['schema'] == '2' and perform_validation:
            validate(content, MAIN_JSONSCHEMA)

        content = kfrozendict.freeze(content)

        self.perform_renames = True
        self.perform_transformations = True

        self.strip_unknown = strip_unknown

        self.perform_validation = perform_validation

        self.default_tx = False

        try:
            initial_schema = content['schema']
        except KeyError as err:
            raise ValueError('content.schema not found')


        # "transformations" represent changes that need to be made to a survey
        # to load it into this "Content" object. They are described in the schema
        #  * The "rw" function is called on load
        #  * The "fw" function is called on export
        (schema, transformations) = unpack_schema_string(initial_schema)

        transformations.reverse()
        content = content.copy(schema=schema)

        transformer_list = TransformerList([
            TRANSFORMERS[tname]
            for tname in transformations
        ])

        # this will add some transformations onto the list
        # mainly to migrate stuff like choice-lists away from schema:'1'
        for transformer_name in DEFAULT_TRANSFORMERS.get(schema, []):
            transformer_list.ensure(TRANSFORMERS[transformer_name])

        content = transformer_list.rw(content)

        self._v = schema
        self.schema = self._v

        self.data = kfrozendict.freeze(content)

        if self._v == '1':
            self.load_content_schema_1()
        elif self._v == '2':
            self.load_content_schema_2()

        if self.perform_validation:
            self._validate_export()

    def _validate_export(self):
        validate(self.export(schema='2'), MAIN_JSONSCHEMA)

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

    def export(self, schema='2', flat=FLAT_DEFAULT, remove_nulls=False,
               immutable=False):
        self.export_params = SimpleNamespace(remove_nulls=remove_nulls)
        result = None
        designated_schema = schema
        # schema string is in the format:
        # "schema+transformation1+transformation2"
        (schema, transformations) = unpack_schema_string(designated_schema)

        if schema == '1':
            if flat == False:
                raise ValueError('schema=1, flat=False is not an option')
            result = self.to_v1_structure()
        else:
            result = self.to_structure(schema=schema, flat=flat)

        result = kfrozendict.freeze(result)
        schemas = [schema]
        for transformation in transformations:
            transformer = TRANSFORMERS[transformation]
            if hasattr(transformer, 'TRANSFORMER'):
                transformer = transformer.TRANSFORMER
            _t_result = transformer.fw(result)
            if _t_result is not None:
                result = _t_result
                schemas.append(transformation)

        result = result.copy(schema='+'.join(schemas))
        if immutable:
            return result
        return kfrozendict.unfreeze(
            result.copy(schema='+'.join(schemas))
        )

    def _tanchors(self, **kwargs):
        '''
        this is used primarily in tests.
        It returns a list of anchors and/or types so that tests can verify
        the structure is exported as intended
        '''
        default_anchor = '$kuid' if kwargs.get('schema') == 1 else '$anchor'
        _key = kwargs.pop('key', default_anchor)
        def get_anchors(row, _path=None):
            if _path is None:
                _path = tuple()
            if len(_path) > 0:
                if _key not in row:
                    raise ValueError('no key in row')
                ank = row.get(_key, 'z')
                yield '.'.join((_path + (ank,))[1:])
            for subrow in row.get('rows', []):
                for subanchor in get_anchors(subrow,
                                             _path=_path + (row.get(_key, 'xx'),)
                                             ):
                    yield subanchor
        return list(
            get_anchors(
                {'rows': self.export(**kwargs)['survey'],
                 '$anchor': ''}
            )
        )

    def to_structure(self, schema='2', flat=FLAT_DEFAULT):
        return _sans_empty_values(kfrozendict.unfreeze({
            'schema': schema,
            'translations': self.txs.to_list(schema=schema),
            'survey': self.survey.to_list(schema=schema, flat=flat),
            'choices': self.choices.to_dict(schema=schema),
            'settings': self.settings.to_dict(schema=schema),
            'metas': self.metas.to_dict(schema=schema),
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
        self._data_settings = self.data.get('settings')

        self.metas = Metas(content=self)
        self.txs = TxList(content=self)
        self.ensure_default_language()
        self.choices = ChoiceLists(content=self)
        self.survey = Surv(content=self)
        self.settings = Settings(content=self)

    def to_v1_structure(self):
        return kfrozendict.unfreeze({
            'schema': '1',
            'translated': sorted(self._tx_columns),
            'translations': self.txs.to_v1_strings(),
            'survey': self.survey.to_list(schema='1', flat=FLAT_DEFAULT),
            'choices': self.choices.to_old_arr(),
            'settings': self.settings.to_dict(schema='1'),
        })
