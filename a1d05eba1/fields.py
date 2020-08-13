from .utils.kfrozendict import kfrozendict
from .utils.kfrozendict import assertfrozen
from .utils import kassertfrozen



class RawValue:
    def __init__(self, txv, value):
        self.txv = txv
        if isinstance(value, (dict, kfrozendict)):
            if 'string' in value:
                self.value = value['string']
        elif isinstance(value, (list, tuple)):
            raise ValueError('RawValue should be a dict or string')
        else:
            self.value = value

    def to_string(self):
        return self.value

    def to_dict(self):
        return self.value

class TranslatedVal:
    def __init__(self, content, key, val):
        self.content = content
        assert isinstance(key, str)
        self.key = key
        self.load(val)

    def load(self, val):
        if self.content.schema_version == '1':
            self.vals = self.load_from_old_vals(val)
        elif self.content.schema_version == '2':
            self.vals = self.load_from_new_vals(val)

    def __repr__(self):
        return '<Tx {}={}>'.format(
            self.key,
            self.vals,
        )

    def load_from_new_vals(self, txvals):
        vals = kfrozendict()
        if isinstance(txvals, str):
            raise ValueError('label cannot be a string when schema==2')
        for (tx_anchor, val) in txvals.items():
            vals = vals.copy(**{tx_anchor: RawValue(self, val)})
        return vals

    def load_from_old_vals(self, txvals):
        vals = tuple()
        if isinstance(txvals, str):
            _arr = [None] * len(self.content.txs)
            _fallback_tx_index = self.content.fallback_tx_index()
            _arr[_fallback_tx_index] = txvals
            txvals = _arr
        assert len(txvals) == len(self.content.txs)
        for (tx, val) in zip(self.content.txs, txvals):
            vals = vals + (
                (tx.anchor, RawValue(self, val)),
            )
        return vals

    @kassertfrozen
    def dict_key_vals_new(self):
        vals = {}
        dvals = dict(self.vals)
        for tx in self.content.txs:
            tx_anchor = tx.anchor
            value = dvals[tx_anchor].to_dict()
            assert not isinstance(value, (list, tuple))
            if value is not None:
                vals[tx_anchor] = value
        return (self.key, kfrozendict(vals))

    def dict_key_vals_old(self, renames=None):
        if renames is None:
            renames = {}
        ovals = ()
        dvals = dict(self.vals)
        for tx in self.content.txs:
            value = dvals[tx.anchor].to_string()
            assertfrozen(value)
            assert not isinstance(value, (list, tuple))
            ovals = ovals + (
                value,
            )
        key = self.key
        if key in renames:
            key = renames[key]
        yield (key, ovals)

class UntranslatedVal:
    def __init__(self, content, key, val):
        self.content = content
        self.key = key
        self.val = val

    def __repr__(self):
        return '<{}={}>'.format(
            self.key,
            self.val,
        )

    @kassertfrozen
    def dict_key_vals_new(self):
        return (self.key, self.val)

    def dict_key_vals_old(self, renames=None):
        if renames is None:
            renames = {}
        key = self.key
        if key in renames:
            key = renames[key]
        yield (key, self.val)
