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
        self._initial_name = name
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
        _name = self.name
        if _name is None:
            _name = ''

        obj = {
            'name': _name,
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

    def to_v1_strings(self):
        return [tx.as_string_or_null() for tx in self._tuple]

    def reorder(self):
        # put the default translation first
        default_tx = self.content.default_tx
        if default_tx and len(self._tuple) > 0:
            others = (tx for tx in self._tuple if tx is not default_tx)
            self._tuple = (default_tx,
                           *others)

    def _load_from_strings(self):
        self._tx_strings = self.content.data.get('translations', [])
        tx_name_lookup = {}
        for (index, txname) in enumerate(self._tx_strings):
            assert txname is None or isinstance(txname, str)
            tx = Translation(name=txname, _tx_index=index)
            if txname is not None:
                tx.load_string(txname)
            if tx.name in tx_name_lookup:
                errmsg = '{} "{}" and "{}"'.format(
                    'Inconsistent translation columns:',
                    tx_name_lookup[tx.name]._initial_name,
                    tx._initial_name,
                )
                raise ValueError(errmsg)
            tx_name_lookup[tx.name] = tx

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
