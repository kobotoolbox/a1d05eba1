import re
import string

from .base_component import SurveyComponentWithTuple
from ..utils.kfrozendict import kfrozendict
from ..utils import kassertfrozen

from ..exceptions import TranslationImportError

LETTERS = string.ascii_lowercase + string.digits
NULL_TRANSLATION = 'NULL_TRANSLATION'

def load_string(name):
    mtch = re.match('(.*)\\s*\\((.*)\\)\\s*', name)
    if mtch:
        [_name, locale] = mtch.groups()
        return (_name.strip(), locale)
    else:
        return (name.strip(), None)


class Translation:
    def __init__(self, name,
                 anchor=None,
                 locale=None,
                 _initial=None,
                 _tx_index=None):
        assert name is not None
        assert name != ''
        self._initial_name = _initial
        self.name = name
        if name in ['', None]:
            self.name = NULL_TRANSLATION
        if anchor is None and _tx_index is None:
            raise ValueError('Translation needs "$anchor"')
        elif anchor is None:
            anchor = 'tx{}'.format(_tx_index)
        self.anchor = anchor
        self.locale = locale
        if not self.locale:
            self._name_plus_locale = self.name
            self._aliases = (self.name,)
        else:
            assert self.name is not NULL_TRANSLATION
            self._name_plus_locale = '{} ({})'.format(self.name, self.locale)
            self._aliases = (
                self.name,
                self.locale,
                self._name_plus_locale
            )

    def as_string_or_null(self):
        # for exporting to schema='1'
        if self.name is NULL_TRANSLATION:
            return None
        return self._name_plus_locale

    @kassertfrozen
    def as_frozen_dict(self):
        obj = {'$anchor': self.anchor,}
        obj['name'] = '' if self.name is NULL_TRANSLATION else self.name
        if self.locale:
            obj['locale'] = self.locale
        return kfrozendict(obj)


class TxList(SurveyComponentWithTuple):
    def load(self, **kwargs):
        if self.content.schema_version == '1':
            self._load_from_strings(**kwargs)
        elif self.content.schema_version == '2':
            self._load_from_new_list(**kwargs)

    def set_initial_by_string(self, tx_str):
        _initial_tx = False
        for tx in self:
            if tx_str in tx._aliases:
                _initial_tx = tx
                break
        if _initial_tx:
            self.set_first(_initial_tx)

    def to_v1_strings(self):
        return [tx.as_string_or_null() for tx in self._tuple]

    def to_v1_strings_tuple(self):
        out = ()
        for tx in self._tuple:
            out = out + (tx.as_string_or_null(),)
        return out

    def set_first(self, first):
        assert isinstance(first, Translation) and first in self
        others = (tx for tx in self if tx is not first)
        self._tuple = (first,) + tuple(others)

    @property
    def names(self):
        return [tx.name for tx in self]

    @property
    def anchors(self):
        return (tx.anchor for tx in self)

    def _load_from_strings(self):
        self._tx_strings = self.content.data.get('translations', [])
        tx_name_lookup = {}
        for (index, txname) in enumerate(self._tx_strings):
            _initial = txname
            if txname in [None, '']:
                txname = NULL_TRANSLATION
            assert txname != ''
            txanchor = None
            locale = None
            if txname != NULL_TRANSLATION:
                txname, locale = load_string(txname)
                txanchor = locale
            tx = Translation(name=txname, anchor=txanchor, locale=locale, _tx_index=index, _initial=_initial)
            if tx.name in tx_name_lookup:
                errmsg = '{} "{}" and "{}"'.format(
                    'Conflicting translation columns:',
                    tx_name_lookup[tx.name]._initial_name,
                    tx._initial_name,
                )
                raise TranslationImportError(errmsg)
            tx_name_lookup[tx.name] = tx

            self._tuple = self._tuple + (
                tx,
            )
        if len(self._tuple) == 1:
            # not the "immutable" way
            self._tuple[0].is_default = True

    def _load_from_new_list(self):
        array_of_txs = self.content.data.get('translations', [])
        bump_to_first = False
        for (index, tx) in enumerate(array_of_txs):
            (tx, initial_) = tx.popout('initial', False)

            if tx['name'] == '':
                tx = tx.copy(name=NULL_TRANSLATION, _initial='')

            if '$anchor' in tx:
                (tx, anchor) = tx.popout('$anchor')
                tx = tx.copy(anchor=anchor)

            cur_translation = Translation(**tx)
            if initial_:
                bump_to_first = cur_translation

            self._tuple = self._tuple + (
                cur_translation,
            )
        if bump_to_first:
            self.set_first(bump_to_first)

    def to_tuple(self, schema):
        return tuple(tx.as_frozen_dict() for tx in self._tuple)
