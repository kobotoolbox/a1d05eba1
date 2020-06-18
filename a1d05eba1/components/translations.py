import re
import string
import random

from ..utils.kfrozendict import kfrozendict
from ..exceptions import TranslationImportError

from .base_component import SurveyComponentWithTuple, SurveyComponentWithDict


LETTERS = string.ascii_lowercase + string.digits


class Translation:
    def __init__(self, name,
            anchor=None,
            locale=None,
            _tx_index=None):

        self.name = name

        if anchor is None and _tx_index is None:
            raise ValueError('Translation needs "$anchor"')
        elif anchor is None:
            anchor = 'tx{}'.format(_tx_index)
        self.anchor = anchor
        self.locale = locale

    def load_string(self, name):
        mtch = re.match('(.*)\\s+\\((.*)\\)\\s*', name)
        if mtch:
            [_name, locale] = mtch.groups()
            self.name = _name
            self.locale = locale
            self.anchor = locale

    def as_string_or_null(self):
        # for exporting to schema='1'
        if self.name is None:
            return None
        out = self.name
        if self.locale:
            out += ' ({})'.format(self.locale)
        return out

    def as_object(self, is_default=False):
        # assert self.code == self.anchor
        obj = {
            'name': self.name,
            '$anchor': self.anchor,
        }
        if self.locale:
            obj['locale'] = self.locale
        if is_default:
            obj['default'] = True
        return obj


class TxList(SurveyComponentWithTuple):
    def load(self, **kwargs):
        if self.content.schema == '1':
            self._load_from_strings(**kwargs)
        elif self.content.schema == '2':
            self._load_from_new_list(**kwargs)

    # def __index__(self, nn):
    #     return self._tuple.__index__(nn)

    def validate(self):
        if hasattr(self, '_tx_strings'):
            self._validate_tx_names(self._tx_strings)
        else:
            # names = [tx.name for tx in self._tuple]
            codes = [tx.code for tx in self._tuple]
            self._validate_tx_names(self.get_ordered_names())
            self._validate_codes(codes)

    def _validate_codes(self, codes):
        existing_codes = tuple()
        for code in codes:
            if code in [None, '']:
                raise TranslationImportError('Invalid Translation code: {}'.format(code))
            if code in existing_codes:
                raise TranslationImportError('Duplicate Tx Code: {}'.format(code))
            existing_codes = existing_codes + (
                code,
            )

    def _validate_tx_names(self, txnames):
        # tx strings are imported in schema=1 like
        # ['english', 'german', None]
        has_null = False
        existing_tx_names = tuple()
        if len(txnames) is 0:
            raise TranslationImportError('At least one translation must exist')
        null_count = 0
        for tx in txnames:
            if tx is None:
                null_count += 1
            elif tx == '':
                raise TranslationImportError('Invalid Translation name: ""')
            else:
                if tx in existing_tx_names:
                    raise TranslationImportError('Duplicate Tx name: {}'.format(tx))
                existing_tx_names = existing_tx_names + (tx,)
        if null_count > 1:
            raise TranslationImportError('Only one "null" translation can exist')

    def get_ordered_names(self):
        return [tx.name for tx in self._tuple]

    def get_codes(self):
        return [tx.name for tx in self._tuple]

    def to_v1_strings(self):
        return [tx.as_string_or_null() for tx in self._tuple]

    # @property
    # def default_index(self):
    #     return self._tuple.index(self.content.default_tx)
    #
    def reorder(self):
        # put the default translation first
        default_tx = self.content.default_tx
        if default_tx and len(self._tuple) > 0:
            others = (tx for tx in self._tuple if tx is not default_tx)
            self._tuple = (default_tx,
                           *others)

    def _load_from_strings(self):
        self._tx_strings = self.content.data.get('translations', [])
        for (index, txname) in enumerate(self._tx_strings):
            assert txname is None or isinstance(txname, str)
            tx = Translation(name=txname, _tx_index=index)
            if txname is not None:
                tx.load_string(txname)
            self._tuple = self._tuple + (
                tx,
            )
        if len(self._tuple) is 1:
            # not the "immutable" way
            self._tuple[0].is_default = True

    def _load_from_new_list(self):
        array_of_txs = self.content.data.get('translations')
        for (index, tx) in enumerate(array_of_txs):
            if 'uicode' in tx:
                (tx, locale) = tx.popout('uicode')
                tx = tx.copy(locale=locale)
            if 'code' in tx:
                (tx, code) = tx.popout('code')
                tx = tx.copy(**{
                    '$anchor': code
                })
            #     raise Exception('no code')
            defaultval = False
            if 'default' in tx:
                (tx, defaultval) = tx.popout('default')

            if '$anchor' in tx:
                (tx, anchor) = tx.popout('$anchor')
                tx = tx.copy(anchor=anchor)

            cur_translation = Translation(**tx)

            if defaultval and not self.content.default_tx:
                self.content.default_tx = cur_translation

            self._tuple = self._tuple + (
                cur_translation,
            )

    @property
    def codes(self):
        return [tx.anchor for tx in self._tuple]

    def to_list(self, schema):
        objs = []
        default_tx = self.content.default_tx
        for tx in self._tuple:
            objs.append(tx.as_object(is_default=(tx is default_tx)))
        return objs
