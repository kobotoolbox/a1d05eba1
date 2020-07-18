import json

from .utils.kfrozendict import kfrozendict


class RawValue:
    def __init__(self, txv, value):
        self.txv = txv
        self.value = self._load_value(value)

    def _load_value(self, value):
        if isinstance(value, str):
            return value
        elif isinstance(value, (dict, kfrozendict)):
            if 'string' in value:
                return value['string']
        else:
            return value

    def to_string(self):
        return self.value

    def to_dict(self):
        return self.value

class TranslatedVal:
    def __init__(self, content, key, val, original=None):
        self.content = content
        self.original = original
        assert isinstance(key, str)
        self.key = key
        self.load(val)

    def load(self, val):
        if self.content._v == '1':
            self.vals = self.load_from_old_vals(val)
        elif self.content._v == '2':
            self.vals = self.load_from_new_vals(val)

    def __repr__(self):
        return '<Tx {}={}>'.format(
            self.key,
            self.vals,
        )

    def load_from_new_vals(self, txvals):
        vals = kfrozendict()
        for (tx_anchor, val) in txvals.items():
            vals = vals.copy(**{tx_anchor: RawValue(self, val)})
        return vals

    def load_from_old_vals(self, txvals):
        vals = tuple()
        if isinstance(txvals, str):
            _arr = [None] * len(self.content.txs)
            _dtx_index = self.content.txs.index(self.content.default_tx)
            _arr[_dtx_index] = txvals
            txvals = _arr
        assert len(txvals) == len(self.content.txs)
        for (tx, val) in zip(self.content.txs, txvals):
            vals = vals + (
                (tx.anchor, RawValue(self, val)),
            )
        return vals

    def dict_key_vals_new(self):
        _oldvals = {}
        dvals = dict(self.vals)
        for tx in self.content.txs:
            tx_anchor = tx.anchor
            value = dvals[tx_anchor].to_dict()
            if value is not None:
                _oldvals[tx_anchor] = value
        return (self.key, _oldvals)

    def dict_key_vals_old(self, renames=None):
        if renames is None:
            renames = {}
        _oldvals = []
        dd = dict(self.vals)
        for tx in self.content.txs:
            value = dd[tx.anchor].to_string()
            _oldvals.append(value)
        key = self.key
        if key in renames:
            key = renames[key]
        yield (key, _oldvals)

class UntranslatedVal:
    def __init__(self, content, key, val, original=None):
        self.content = content
        self.key = key
        self.val = val

    def __repr__(self):
        return '<{}={}>'.format(
            self.key,
            self.val,
        )

    def dict_key_vals_old(self, renames=None):
        if renames is None:
            renames = {}
        key = self.key
        if key in renames:
            key = renames[key]
        yield (key, self.val)

    def dict_key_vals_new(self):
        return (self.key, self.val)
