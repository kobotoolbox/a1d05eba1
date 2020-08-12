from ..utils.kfrozendict import kfrozendict
from ..utils.anchor_generator import anchor_generator

from ..fields import UntranslatedVal, TranslatedVal
from ..exceptions import (
    DuplicateAnchorError,
    MissingAnchorError,
    MissingAlternateAnchorError,
)


RAND_ANCHOR_KEY = '!RAND'


class SurveyComponentBase:
    def __init__(self, *args, **kwargs):
        self.content = kwargs.pop('content')
        # tbd how we use this
        self._additionals = kfrozendict()
        super().__init__()

        if hasattr(self, 'preload'):
            self.preload(**kwargs)

        if hasattr(self, 'adjust_kwargs'):
            kwargs = self.adjust_kwargs(kwargs)

        if hasattr(self, 'load'):
            self.load(**kwargs)

        load_schema_fn = 'load_from_{}'.format(self.content.schema_version)
        if hasattr(self, load_schema_fn):
            schema_specific_loading_function = getattr(self, load_schema_fn)
            schema_specific_loading_function(**kwargs)

        if hasattr(self, 'postload'):
            self.postload(**kwargs)

    def __repr__(self):
        data_descriptor = self._data_descriptor
        return '<%s%s %s>' % (self.__class__.__name__,
                               data_descriptor,
                               repr(self._insides),
                               )

    def __getitem__(self, index):
        return self._insides.__getitem__(index)


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

    def _popout_anchor(self, row):
        '''
        allows components with a specified FALLBACK_ANCHOR_KEY (e.g. "name")
        to be indexed by their "name" column instead of their "$anchor"

        stores this column as "self._anchor"

        receives:
            a <kfrozendict()> with "$anchor" or fallback value (eg "name")
        returns:
            a <kfrozendict()> without "$anchor"

        * sets the value of "self._anchor"
        * ensures that "self._anchor" is unique
        '''
        initial_row = row

        if '$anchor' in row:
            (row, anchor) = row.popout('$anchor')
        else:
            raise MissingAnchorError(row=initial_row.unfreeze(),
                                     klass=self.__class__.__name__)
        if anchor == RAND_ANCHOR_KEY:
            anchor = anchor_generator()

        self.register_component_by_anchor(anchor, initial_row)
        return row

    def register_component_by_anchor(self, anchor, initial_row):
        self._anchor = anchor
        if self._anchor in self.content._anchored_components:
            other = self.content._anchored_components[self._anchor]
            raise DuplicateAnchorError(
                klass=self.__class__.__name__,
                key=self.FALLBACK_ANCHOR_KEY,
                row1=other._data.unfreeze(),
                row2=self._data.unfreeze(),
            )
        self.content._anchored_components[self._anchor] = self


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
