from jsonschema import validate as jsonschema_validate

from .utils.kfrozendict import kfrozendict
from .utils.kfrozendict import unfreeze, deepfreeze

# components
from .components import Surv
from .components import ChoiceLists
from .components import TxList
from .components import Settings
from .components import Metas

from .build_schema import MAIN_JSONSCHEMA

from .transformations import TransformerList

from .export_configs import XlsformExport, KoboXlsformExport
from .export_configs import DefaultExportConfigs
from .export_configs import DefaultExportConfigsSchema1

from .schema_properties import TRANSLATABLE_SURVEY_COLS

METAS = MAIN_JSONSCHEMA['$defs']['metas']

SCHEMAS = [
    '1',
    '2',
]

def _sans_empty_values(obj):
    # remove keys with 'None' as a value in the returned dict
    for delete_key in [k for (k, v) in obj.items() if v is None]:
        del obj[delete_key]
    return obj


class Content:
    # can be overridden in subclasses
    schema_string = None            # e.g. '2'
    input_schema = None             # A valid jsonschema
    strip_unknown_values = True     # Ignore unknown properties

    # survey attributes pulled from settings
    initial_tx = False     # "default_translation" pulled from settings
    fallback_tx = False

    transformers = ()

    META_TYPES = set(METAS['properties'].keys())

    EXPORT_CONFIGS = DefaultExportConfigs
    EXPORT_CONFIGS_SCHEMA_1 = DefaultExportConfigsSchema1

    export_configs = None

    def __init__(self,
                 content,
                 validate=False,
                 extra_validate=False,
                 debug=False,
                 strip_unknown=None,
                 ):

        self._known_columns = tuple()
        self._anchored_components = {}

        perform_validation = validate
        if self.schema_string:
            if isinstance(content, kfrozendict):
                content = content.copy(schema=self.schema_string)
            else:
                content['schema'] = self.schema_string
        self.validate_required_properties(content)
        if content['schema'] == '2' and perform_validation:
            jsonschema_validate(unfreeze(content), MAIN_JSONSCHEMA)

        content = deepfreeze(content)

        self.perform_renames = True
        self.perform_transformations = True

        self.strip_unknown_values = strip_unknown
        self.perform_validation = perform_validation

        try:
            initial_schema = content['schema']
        except KeyError:
            raise ValueError('content.schema not found')

        # "transformations" represent changes that need to be made to a survey
        # to load it into this "Content" object. They are described in the schema
        #  * The "rw" function is called on load
        #  * The "fw" function is called on export
        schema = initial_schema
        if schema == '1' and 'translations' in content and \
                len(content['translations']) > 0:
            tx1 = content['translations'][0]
            if isinstance(tx1, (dict, kfrozendict)):
                raise ValueError('schema is 1 so translation should be a string or None')
        self._load_content(content.copy(schema=schema),
                           schema,
                           debug,
                           )
        if extra_validate:
            self.validate_export()

    def _load_content(self, content,
                      schema,
                      debug,
                      ):
        content = TransformerList(self.transformers,
                                  debug=debug,
                                  name=self.__class__.__name__,
                                  ).rw(content)

        if 'choices' not in content:
            content = content.copy(choices=kfrozendict())

        # if this assertion fails then the content has not been transformed
        # properly
        assert isinstance(content['choices'], (dict, kfrozendict))

        self.schema_version = schema
        self.data = deepfreeze(content)

        if self.schema_version == '1':
            self.load_content_schema_1()
        elif self.schema_version == '2':
            self.load_content_schema_2()


    def validate_required_properties(self, content):
        # initial, very basic test of structure
        if 'schema' not in content:
            raise ValueError('content.schema must be a string')
        if 'survey' not in content:
            raise ValueError('content.survey[] is required')

        # if class has an "input_schema"
        if self.input_schema:
            cdict = content
            if isinstance(content, kfrozendict):
                cdict = content.unfreeze()
            self.__class__.validate_input_schema(cdict)

    @classmethod
    def validate_input_schema(kls, content):
        if kls.input_schema:
            jsonschema_validate(content, kls.input_schema)

    def validate_export(self):
        jsonschema_validate(self.export(), MAIN_JSONSCHEMA)

    def export(self, schema='2', **kwargs):
        return self.export_to(schema, **kwargs)

    def export_to(self, schema, **kwargs):
        if schema == 'xlsform':
            return self.export_by_config(XlsformExport(**kwargs))
        elif schema == 'koboxlsform':
            return self.export_by_config(KoboXlsformExport(**kwargs))
        elif schema == '2':
            return self.export_by_config(self.EXPORT_CONFIGS(**kwargs))
        elif schema == '1':
            return self.export_by_config(self.EXPORT_CONFIGS_SCHEMA_1(**kwargs))
        raise ValueError('Unknown export schema')

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
        result = deepfreeze(result)
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

    def to_structure(self, export_configs):
        flat = export_configs.flat
        schema = export_configs.schema
        return _sans_empty_values(unfreeze({
            'schema': schema,
            'translations': self.txs.to_list(schema=schema),
            'survey': self.survey.to_list(schema=schema, flat=flat),
            'choices': self.choices.to_dict(schema=schema),
            'settings': self.settings.to_dict(export_configs),
            'metas': self.metas.to_dict(schema=schema),
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
        (self._data_settings, _initial_tx) = \
            self.data.get('settings').popout('default_language', False)
        self.metas = Metas(content=self)
        self.txs = TxList(content=self)
        self.choices = ChoiceLists(content=self)
        self.survey = Surv(content=self)
        self.settings = Settings(content=self)
        if _initial_tx:
            self.txs.set_initial_by_string(_initial_tx)

    def to_v1_structure(self, export_configs):
        return unfreeze({
            'schema': '1',
            'translated': sorted(self._tx_columns),
            'translations': self.txs.to_v1_strings(),
            'survey': self.survey.to_list(schema='1', flat=True),
            'choices': self.choices.to_old_arr(),
            'settings': self.settings.to_dict(export_configs),
        })
