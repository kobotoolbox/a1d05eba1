from .utils.validate import jsonschema_validate
from .utils.kfrozendict import kfrozendict
from .utils.kfrozendict import unfreeze
from .utils.kfrozendict import deepfreeze
from .utils.kfrozendict import assertfrozen
from .utils import kassertfrozen

from .components import Surv
from .components import ChoiceLists
from .components import TxList
from .components import Settings
from .components import Metas

from .exceptions import ContentValidationError

from .build_schema import MAIN_JSONSCHEMA

from .transformations import TransformerList

from .export_configs import ExportConfigs
from .export_configs import XlsformExport, KoboXlsformExport
from .export_configs import DefaultExportConfigs
from .export_configs import DefaultExportConfigsSchema1

from .schema_properties import TRANSLATABLE_SURVEY_COLS
from .schema_properties import TRANSLATABLE_MEDIA_COLS

METAS = MAIN_JSONSCHEMA['$defs']['metas']

SCHEMAS = [
    '1',
    '2',
]


@kassertfrozen
def _sans_empty_values(obj):
    # remove keys with 'None' as a value in the returned dict
    delete_keys = []
    for key, val in obj.items():
        if val is None:
            delete_keys.append(key)
    for delete_key in delete_keys:
        obj = obj.without(delete_key)
    return obj


class BaseContent:
    # can be overridden in subclasses
    from_schema_string = None       # to import a schema from a specific string
    schema_string = None            # e.g. '2'
    input_schema = None             # A valid jsonschema
    strip_unknown_values = True     # Ignore unknown properties
    txs = None
    metas = None
    survey = None
    choices = None
    settings = None
    anchored_components = kfrozendict()
    _known_columns = ()

    # survey attributes pulled from settings
    _data_settings = None
    _media_files = None
    initial_tx = False     # "default_translation" pulled from settings
    fallback_tx = False

    transformers = ()

    META_TYPES = set(METAS['properties'].keys())

    EXPORT_CONFIGS = DefaultExportConfigs
    EXPORT_CONFIGS_SCHEMA_1 = DefaultExportConfigsSchema1

    export_configs = None

    @property
    def schema_version(self):
        return self.data['schema']

    def __init__(self,
                 content,
                 validate=False,
                 extra_validate=False,
                 debug=False,
                 strip_unknown=None,
                 ):
        self.perform_renames = True
        self.perform_transformations = True
        self.strip_unknown_values = strip_unknown
        self.perform_validation = validate

        content = deepfreeze(content)

        if self.from_schema_string:
            if self.from_schema_string != content['schema']:
                msg = 'from_schema_string does not match'
                raise ContentValidationError(msg)
            if not self.schema_string:
                msg = 'from_schema_string is set but not schema_string'
                raise ValueError(msg)
            content = content.copy(schema=self.schema_string)

        # schema_string is an optional class-specified schema
        if self.schema_string:
            if 'schema' in content:
                assert content['schema'] == self.schema_string
            content = content.copy(schema=self.schema_string)
        elif 'schema' not in content:
            raise ValueError('No fallback schema_string set')
        elif content['schema'] not in ['1', '2']:
            _schema = content['schema']
            raise ValueError(f'Unrecognized schema: {_schema}')

        if self.input_schema:
            jsonschema_validate(content, self.input_schema)

        if 'survey' not in content or not isinstance(content['survey'], tuple):
            raise ValueError('content.survey must be a list')

        if validate and content['schema'] == '2':
            jsonschema_validate(content, MAIN_JSONSCHEMA)

        # "transformations" represent changes that need to be made to a survey
        # to load it into this "Content" object. They are described in the schema
        #  * The "rw" function is called on load
        #  * The "fw" function is called on export
        content = TransformerList(self.transformers,
                                  debug=debug,
                                  name=self.__class__.__name__,
                                  ).rw(content)
        if 'choices' not in content:
            content = content.copy(choices=kfrozendict())
        self.data = content

        if self.schema_version == '1':
            self.load_content_schema_1()
        elif self.schema_version == '2':
            self.load_content_schema_2()
        else:
            raise ValueError(f'unknown schema: {self.schema_version}')
        # if this assertion fails then the content has not been transformed
        # properly
        assert isinstance(content['choices'], (dict, kfrozendict))
        if extra_validate:
            self.validate_export()

    def validate_required_properties(self, content):
        # initial, very basic test of structure
        if 'schema' not in content:
            raise ValueError('content.schema must be a string')
        if 'survey' not in content:
            raise ValueError('content.survey[] is required')

    @classmethod
    def validate_input_schema(kls, content):
        if kls.input_schema:
            jsonschema_validate(content, kls.input_schema)

    @property
    def media_files(self):
        if self._media_files is None:
            files = []
            def pull_files(row, cols):
                keys = set(row._keys)
                for col in keys.intersection(cols):
                    vals = row[col]
                    for value in vals.values():
                        files.append(value)
            for row in self.survey:
                pull_files(row, TRANSLATABLE_MEDIA_COLS['survey'])
            for choices in self.choices.values():
                for choice in choices:
                    pull_files(choice, TRANSLATABLE_MEDIA_COLS['choices'])
            self._media_files = tuple(files)
        return self._media_files

    def validate_export(self):
        jsonschema_validate(self.export(), MAIN_JSONSCHEMA)

    def export(self, schema='2', **kwargs):
        return self.export_to(schema, **kwargs)

    def export_to(self, schema_or_configs, **kwargs):
        if isinstance(schema_or_configs, str):
            schema = schema_or_configs
            export_configs = {
                'xlsform': XlsformExport,
                'koboxlsform': KoboXlsformExport,
                '1': self.EXPORT_CONFIGS_SCHEMA_1,
                '2': self.EXPORT_CONFIGS,
            }[schema](**kwargs)
        else:
            configs_kls = schema_or_configs
            assert issubclass(configs_kls, ExportConfigs)
            export_configs = configs_kls(**kwargs)
        return self.export_by_config(export_configs)

    def export_by_config(self, export_configs):
        result = self._export(export_configs)
        return self.export_configs.fw(result).unfreeze()

    def _export(self, export_configs):
        # Receives an ExportConfigs argument as a parameter
        # Returns an immutable structure
        self.export_configs = _ec = export_configs
        schema = _ec.schema
        assert schema in ['1', '2']

        result = None
        if schema == '1':
            if not _ec.flat:
                raise ValueError('cannot export(schema=1, flat=False)')
            result = self.to_v1_structure(export_configs)
        else:
            result = self.to_structure(export_configs)
        assertfrozen(result)
        result = result.copy(schema=schema)

        if _ec.remove_nulls:
            for key in ['settings', 'metas', 'choices']:
                if len(result[key]) == 0:
                    result = result.without(key)
        return result

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

    def _tanchors(self, **kwargs):
        '''
        this is used primarily in tests.
        It returns a list of anchors and/or types so that tests can verify
        the structure is exported as intended
        '''
        default_anchor = '$kuid' if kwargs.get('schema') == '1' else '$anchor'
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

    @kassertfrozen
    def to_structure(self, export_configs):
        flat = export_configs.flat
        schema = export_configs.schema
        return _sans_empty_values(kfrozendict({
            'schema': schema,
            'translations': self.txs.to_tuple(schema=schema),
            'survey': self.survey.to_tuple(schema=schema, flat=flat),
            'choices': self.choices.to_frozen_dict(schema=schema),
            'settings': self.settings.to_frozen_dict(export_configs),
            'metas': self.metas.to_frozen_dict(schema=schema),
        }))

    def load_content_schema_2(self):
        content = self.data
        self._data_settings = self.data.get('settings', {})
        self.metas = Metas(content=self)
        self.txs = TxList(content=self)

        _ctmp = content.get('choices', {})
        self.choices = ChoiceLists(content=self)

        self.survey = Surv(content=self)
        self.settings = Settings(content=self)

    def fallback_tx_index(self):
        if self.fallback_tx is False:
            return 0
        return self.txs.index(self.fallback_tx)

    def load_content_schema_1(self):
        if 'translations' not in self.data:
            self.data = self.data.copy(translations=(None,))
        (self._data_settings, _initial_tx) = \
            self.data.get('settings').popout('default_language', False)
        self.metas = Metas(content=self)
        self.txs = TxList(content=self)
        self.choices = ChoiceLists(content=self)
        self.survey = Surv(content=self)
        self.settings = Settings(content=self)
        if _initial_tx:
            self.txs.set_initial_by_string(_initial_tx)

    @kassertfrozen
    def to_v1_structure(self, export_configs):
        return kfrozendict({
            'schema': '1',
            'translated': tuple(sorted(self._tx_columns)),
            'translations': self.txs.to_v1_strings_tuple(),
            'survey': self.survey.to_tuple(schema='1', flat=True),
            'choices': self.choices.to_old_tuple(),
            'settings': self.settings.to_frozen_dict(export_configs),
        })

class Content(BaseContent):
    schema_string = '2'
    input_schema = MAIN_JSONSCHEMA
