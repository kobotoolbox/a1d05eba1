from jsonschema import validate
from jsonschema.exceptions import ValidationError

from ..utils.kfrozendict import kfrozendict
from ..fields import UntranslatedVal, TranslatedVal


class SurveyComponentBase:
    def __init__(self, *args, **kwargs):
        self.content = kwargs.pop('content')
        super().__init__()

        if hasattr(self, 'preload'):
            self.preload(**kwargs)

        if hasattr(self, 'load'):
            self.load(**kwargs)

        load_schema_fn = 'load_from_{}'.format(self.content.schema)
        if hasattr(self, load_schema_fn):
            schema_specific_loading_function = getattr(self, load_schema_fn)
            schema_specific_loading_function(**kwargs)

        if hasattr(self, 'postload'):
            self.postload(**kwargs)

    # def load(self, **kwargs):
    #     load_schema_fn = 'load_from_{}'.format(self.content.schema)
    #     if hasattr(self, load_schema_fn):
    #         schema_specific_loading_function = getattr(self, load_schema_fn)
    #         schema_specific_loading_function(**kwargs)

    # def unfrozen(self):
    #     return kfrozendict.unfreeze(self._insides)

    def __repr__(self):
        data_descriptor = self._data_descriptor
        return '<%s%s %s>' % (self.__class__.__name__,
                               data_descriptor,
                               repr(self._insides),
                               )

    def __getitem__(self, index):
        return self._insides.__getitem__(index)

        # validate_schema_property = 'v{}_schema'.format(self.content.schema)

        # if self.content.perform_validation:
        #     self.validate()

    # def validate(self):
    #     validate_schema_property = 'v{}_schema'.format(self.content.schema)
    #     hasschema = hasattr(self, validate_schema_property)
    #
    #     if hasattr(self, 'v2_schema') and not hasattr(self, 'jsonschema'):
    #         raise Exception('xxx')
    #         self.v2_schema = ''
    #
    #     if hasattr(self, 'validated_content') and hasschema:
    #         _cur_content = kfrozendict.unfreeze(self.validated_content)
    #         schema = getattr(self, validate_schema_property)
    #         self._validate(_cur_content, schema)
    #     elif self.content.perform_validation:
    #         if hasattr(self, '_tuple'):
    #             for item in self._tuple:
    #                 item.validate()
    #         elif hasattr(self, '_d'):
    #             for (key, val) in self._d.items():
    #                 val.validate()
    # def _validate(self, _content, schema, message=''):
    #     _content = kfrozendict.unfreeze(_content)
    #     try:
    #         validate(_content, schema)
    #     except ValidationError as err:
    #         msg = '\n'.join([
    #             '\n',
    #             message,
    #             self.content.identifier,
    #             repr(self),
    #         ])
    #         err.message += msg
    #         raise err


class SurveyComponentWithTuple(SurveyComponentBase):
    _data_descriptor = '[]'

    def __init__(self, *args, **kwargs):
        self._tuple = tuple()
        super().__init__(*args, **kwargs)

    def __iter__(self):
        return iter(self._tuple)

    @property
    def _insides(self):
        return self._tuple

    def index(self, item):
        return self._tuple.index(item)

    def __len__(self):
        return len(self._tuple)

    def append(self, item):
        self._tuple = self._tuple + (
            item,
        )

class SurveyComponentWithOrderedDict(SurveyComponentBase):
    _data_descriptor = '{[]}'

    def __init__(self, *args, **kwargs):
        self._values = tuple()
        self._keys = tuple()
        super().__init__(*args, **kwargs)

    def set_translated(self, key, val, original=None):
        self.set(key, TranslatedVal(self.content, key, val))

    def set_untranslated(self, key, val, original=None):
        self.set(key, UntranslatedVal(self.content, key, val))

    def __iter__(self):
        return iter(self._values)

    @property
    def _insides(self):
        return self._values

    def __len__(self):
        return len(self._values)

    def has(self, key):
        return key in self._keys

    def set(self, key, value):
        # tbd-- do we need these to be true?
        assert hasattr(value, 'key')
        assert value.key == key
        assert key not in self._keys
        self._keys = self._keys + (key,)
        self._values = self._values + (value,)

class SurveyComponentWithDict(SurveyComponentBase):
    _data_descriptor = '{}'

    def __init__(self, *args, **kwargs):
        self._d = kfrozendict()
        super().__init__(*args, **kwargs)

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    @property
    def _insides(self):
        return self._d

    def items(self):
        return self._d.items()
