import json

from .utils.kfrozendict import kfrozendict


class RawValue:
    def __init__(self, txv, value):
        self.txv = txv
        self.value = self._load_value(value)
        self._type = 'string'

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
        # e.g. { 'string': 'my label'}
        return {
            self._type: self.value,
        }

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
        for (txanchor, val) in txvals.items():
            appendr = {}
            appendr[txanchor] = RawValue(self, val)
            vals = vals.copy(**appendr)
        return vals

    def load_from_old_vals(self, txvals):
        vals = tuple()
        if isinstance(txvals, str):
            raise ValueError('expecting "{}" to be a list'.format(txvals))
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
            anchor = tx.anchor
            _oldvals[anchor] = dvals[tx.anchor].to_dict()
        # assert json.dumps(dvals, sort_keys=True) == json.dumps(_oldvals, sort_keys=True)
        return (self.key, _oldvals)

    def dict_key_vals_old(self, renames=None):
        if renames is None:
            renames = {}
        _oldvals = []
        dd = dict(self.vals)
        for tx in self.content.txs:
            _oldvals.append(dd[tx.anchor].to_string())
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


class ConstraintMessage(TranslatedVal):
    def __init__(self, content, message):
        self.content = content
        self.key = 'constraint_message'
        self.load(message)

    def load_from_old_vals(self, txvals):
        _data = {}
        if isinstance(txvals, str):
            raise Exception('do we land here?')
            # if no translation exists, load it in as the defualt tx
            default_index = self.content.txs.default_index
            txstr = txvals
            txvals = [None] * len(self.content.txs)
            txvals[default_index] = txstr
        for (ii, tx) in enumerate(self.content.txs):
            anchor = tx.anchor
            value = txvals[ii]
            _data[anchor] = RawValue(self, value)
        self._val = _data

    def load_from_new_vals(self, message):
        _data = {}
        for (tx, string) in message.items():
            _data[tx] = RawValue(self, string)
        self._val = _data

    def dict_key_vals_new(self):
        _oldvals = {}
        dvals = dict(self._val)
        for tx in self.content.txs:
            anchor = tx.anchor
            _oldvals[anchor] = dvals[tx.anchor].to_dict()
        return (self.key, _oldvals)

    def dict_key_vals_old(self, renames=None):
        _oldvals = []
        dd = dict(self._val)
        for tx in self.content.txs:
            _oldvals.append(dd[tx.anchor].to_string())
        key = 'constraint_message'
        yield (key, _oldvals)


class RelevantVal:
    SCHEMA_1_ROW_KEYS = ['relevant']
    SCHEMA_2_ROW_KEYS = ['relevant']

    @classmethod
    def pull_from_row(kls, row, content):
        schema = content.schema
        if 'relevant' not in row:
            return
        else:
            yield kls(content, row['relevant'])

    def __init__(self, content, val):
        self.content = content
        self.key = 'relevant'
        if isinstance(val, str):
            self.string = val
        elif isinstance(val, (dict, kfrozendict)):
            self.string = val.get('string')
        self.val = {'string': self.string}

    def dict_key_vals_old(self, renames=None):
        yield ('relevant', self.string)

    def dict_key_vals_new(self):
        return ('relevant', self.val)

class ConstraintVal:
    '''
    Because a row's "constraint_message" is only valid if there is also a
    "constraint", then the two logically should be stored together and validated
    together.

    A constraint looks like one of these structures:

    - string: '${age} > 0'
      message:
        tx0:
          string: "age must be greater than 0"

    # or

    - compile: ["${age}", ">", 0]
      message:
        tx0:
          compile: ["Age must be greater than 0. This is invalid: ", {'$lookup': 'age'}]
    '''

    SCHEMA_1_ROW_KEYS = ['constraint', 'constraint_message']
    SCHEMA_2_ROW_KEYS = ['constraint']

    @classmethod
    def pull_from_row(kls, row, content):
        schema = content.schema

        if 'constraint' not in row:
            return
        if schema == '1':
            constraint_data = {
                'string': row.get('constraint'),
            }
            constraint_val = kls(content, constraint_data)

            cmessage = row.get('constraint_message', None)
            if 'constraint_message' in row:
                constraint_val.set_message(cmessage)
            yield constraint_val
        elif schema == '2':
            constraint = row.get('constraint')
            (constraint, message) = constraint.popout('message')

            constraint_val = ConstraintVal(content, row.get('constraint'))
            if message:
                constraint_val.set_message(message)
            yield constraint_val


    def __init__(self, content, val):
        self.content = content
        self.key = 'constraint'
        self.val = val
        self._string = val.get('string')
        self.msg_txd = False

    def set_message(self, message):
        self.msg_txd = ConstraintMessage(self.content, message)

    def dict_key_vals_old(self, renames=None):
        yield ('constraint', self._string,)

        if self.msg_txd:
            for (k, val) in self.msg_txd.dict_key_vals_old(renames=renames):
                yield ('constraint_message', val,)

    def dict_key_vals_new(self, renames=None):
        val = {'string': self.val.get('string')}
        if self.msg_txd:
            (k, message) = self.msg_txd.dict_key_vals_new()
            val['message'] = message
        return ('constraint', val)
