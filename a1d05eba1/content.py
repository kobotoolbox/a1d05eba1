import re

from jsonschema import validate as jsonschema_validate
from jsonschema.exceptions import ValidationError

from .utils.kfrozendict import kfrozendict
from .utils.kfrozendict import unfreeze, deepfreeze

# components
from .components import Surv
from .components import ChoiceLists
from .components import TxList
from .components import Settings
from .components import Metas

from .build_schema import MAIN_JSONSCHEMA

from .transformations import TRANSFORMERS
from .transformations.xlsform_unwrap_settings_from_list import UnwrapSettingsFromList
from .transformations.xlsform_choices import XlsformChoices
from .transformations.anchors_when_needed import DumpExtraneousAnchors
from .transformations.transformer_list import TransformerList
from .transformations.choices_by_list_name import ChoicesByListName
from .transformations import ALIASES as TRANSFORMER_ALIASES
from .transformations.remove_empty_rows import RemoveEmpties

from .schema_properties import TRANSLATABLE_SURVEY_COLS

FLAT_DEFAULT = True
METAS = MAIN_JSONSCHEMA['$defs']['metas']

SCHEMAS = [
    '1',
    '2',
]

def unpack_schema_string(schema):
    '''
    schema string in the format:
      "1+something+something_else"
    becomes:
      schema="1"
      transformer_names=('something', 'something_else',)
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


class Content:
    initial_tx = False
    fallback_tx = False

    META_TYPES = set(METAS['properties'].keys())

    DEFAULT_TRANSFORMERS_1 = (
        UnwrapSettingsFromList,
        XlsformChoices,
    )
    DEFAULT_TRANSFORMERS_2 = (
        DumpExtraneousAnchors,
    )

    def validate_required_properties(self, content):
        # initial, very basic test of scrtucture
        if 'schema' not in content:
            raise ValueError('content.schema must be a string')
        if 'survey' not in content:
            raise ValueError('content.survey[] is required')

    def __init__(self,
                 content,
                 validate=False,
                 extra_validate=False,
                 debug=False,
                 exports_include_defaults=False,
                 strip_unknown=False,
                 ):

        self._known_columns = tuple()
        self._anchored_components = {}

        perform_validation = validate

        self.validate_required_properties(content)
        if content['schema'] == '2' and perform_validation:
            jsonschema_validate(unfreeze(content), MAIN_JSONSCHEMA)

        content = deepfreeze(content)

        self.perform_renames = True
        self.perform_transformations = True

        self.strip_unknown = strip_unknown

        self.perform_validation = perform_validation

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
        if schema == '1' and 'translations' in content and \
                len(content['translations']) > 0:
            tx1 = content['translations'][0]
            if isinstance(tx1, (dict, kfrozendict)):
                raise ValueError('schema is 1 so translation should be a string or None')
        self._load_content(content.copy(schema=schema),
                            transformations,
                            schema,
                            debug,
                            )
        if extra_validate:
            self.validate_export()


    def _load_content(self, content,
                            transformations,
                            schema,
                            debug,
                            ):
        transformer_list = TransformerList([
            TRANSFORMERS[tname]
            for tname in transformations
        ], debug=debug, root=True)

        # this will add some transformations onto the list
        # mainly to migrate stuff like choice-lists away from schema:'1'
        if schema == '1':
            default_transformers = self.DEFAULT_TRANSFORMERS_1
        elif schema == '2':
            default_transformers = self.DEFAULT_TRANSFORMERS_2

        for transformer in default_transformers:
            transformer_list.ensure(transformer)

        if 'choices' not in content:
            content = content.copy_in(choices={})
        elif isinstance(content['choices'], (list, tuple)):
            content = ChoicesByListName().rw(content)

        assert isinstance(content['choices'], (dict, kfrozendict))

        # only touches survey rows on schema=='1'
        content = RemoveEmpties().rw(content)

        if 'settings' in content and isinstance(content['settings'], (list, tuple)):
            content = UnwrapSettingsFromList().rw(content)

        assert isinstance(content['choices'], (dict, kfrozendict))

        content = transformer_list.rw(content)
        self.schema_version = schema
        self.data = deepfreeze(content)

        if self.schema_version == '1':
            self.load_content_schema_1()
        elif self.schema_version == '2':
            self.load_content_schema_2()

    def validate_export(self):
        _ex = self.export(schema='2')
        jsonschema_validate(_ex, MAIN_JSONSCHEMA)

    def export(self, schema='2',
               flat=FLAT_DEFAULT,
               remove_nulls=False,
               debug=False,
               immutable=False):
        result = None
        specified_export_schema = schema
        # schema string is in the format:
        # "schema+transformation1+transformation2"
        (schema, transformations) = unpack_schema_string(specified_export_schema)

        if schema == '1':
            if not flat:
                raise ArgumentError('cannot export(schema=1, flat=False)')
            result = self.to_v1_structure()
            default_transformers = self.DEFAULT_TRANSFORMERS_1
        else:
            result = self.to_structure(schema=schema, flat=flat)
            default_transformers = self.DEFAULT_TRANSFORMERS_2

        transformer_list = TransformerList([
            TRANSFORMERS[transformation]
            for transformation in transformations
        ], debug=debug, root=True)

        for transformer in default_transformers:
            transformer_list.ensure(transformer)

        result = transformer_list.fw(deepfreeze(result))

        # only affect "schema"="1"
        result = TRANSFORMERS['choices_2_list']().fw(result)
        result = TRANSFORMERS['settings_2_list']().fw(result)

        result = result.copy(schema=specified_export_schema)

        if remove_nulls:
            for key in ['settings', 'metas', 'choices']:
                if len(result[key]) == 0:
                    (result, empty_dict) = result.popout(key)

        if immutable:
            return result
        return result.unfreeze()

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
        return _sans_empty_values(unfreeze({
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

    def to_v1_structure(self):
        return unfreeze({
            'schema': '1',
            'translated': sorted(self._tx_columns),
            'translations': self.txs.to_v1_strings(),
            'survey': self.survey.to_list(schema='1', flat=FLAT_DEFAULT),
            'choices': self.choices.to_old_arr(),
            'settings': self.settings.to_dict(schema='1'),
        })
