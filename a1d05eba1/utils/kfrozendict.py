from collections.abc import Mapping


class kfrozendict(Mapping):
    """
    pulled from pypi's `frozendict` library which
    itself seems to be inspired by https://stackoverflow.com/a/2704866

    this is an immutable wrapper around python dictionaries
    """
    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)
        self._hash = None

    def copy(self, **add_or_replace):
        return self.__class__(self, **add_or_replace)

    def renamed(self, from_key, to_key):
        if from_key not in self:
            return self
        keyvals = []
        for (ikey, ival) in self.items():
            if ikey == from_key:
                ikey = to_key
            keyvals.append(
                (ikey, ival)
            )
        return self.__class__(dict(keyvals))

    def without(self, key, **kwargs):
        content, removed = self.popout(key, **kwargs)
        return content

    def popout(self, key, _default=None):
        val = _default
        keyvals = []
        for (ikey, ival) in self.items():
            if ikey == key:
                val = ival
            else:
                keyvals.append(
                    (ikey, ival)
                )

        return (
            self.__class__(dict(keyvals)),
            val,
        )

    def __getitem__(self, key):
        return self._dict[key]

    def __contains__(self, key):
        return key in self._dict

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, unfreeze(self._dict))

    def __hash__(self):
        if self._hash is None:
            h = 0
            for key, value in self._dict.items():
                h ^= hash((key, value))
            self._hash = h
        return self._hash

    def copy_in(self, **kwargs):
        for (k, val) in kwargs.items():
            kwargs[k] = deepfreeze(val)
        return self.copy(**kwargs)

    def unfreeze(self):
        return unfreeze(self)

    # 'uf' is shorthand for "unfreeze()"
    @property
    def uf(self):
        return self.unfreeze()

    def freeze(self):
        return deepfreeze(self)

def unfreeze(val):
    if isinstance(val, (kfrozendict, dict)):
        return dict([
            (ikey, unfreeze(ival))
            for (ikey, ival) in val.items()
        ])
    elif isinstance(val, (list, tuple)):
        return list([
            unfreeze(ival) for ival in val
        ])
    else:
        return val

def shallowfreeze(val):
    '''
    shallowfreeze does not go deep into the object.
    it might save some time in the long run if we don't keep
    calling (effectively) "deepcopy" everywhere.
    '''
    if isinstance(val, dict):
        return kfrozendict(val)
    elif isinstance(val, list):
        return tuple(val)
    else:
        return val

def deepfreeze(val):
    if isinstance(val, (kfrozendict, dict)):
        return kfrozendict([
            (ikey, deepfreeze(ival))
            for (ikey, ival) in val.items()
        ])
    elif isinstance(val, (list, tuple)):
        return tuple(deepfreeze(ival) for ival in val)
    else:
        return val


class NotFrozenError(ValueError):
    def __init__(self, inner, outer=None):
        msg = (inner, outer) if outer else (inner,)
        super().__init__('\n'.join(msg))

class NotFrozenInnerError(ValueError):
    def __init__(self, inner, arg2=None):
        self.inner = inner
        super().__init__(f'''
        {repr(inner)}
        ''')

def assertfrozen(val):
    try:
        # _assertfrozen(val)
        _shallowassertfrozen(val)
    except NotFrozenInnerError as err:
        raise NotFrozenError(err.inner, outer=val)

def _shallowassertfrozen(val):
    if isinstance(val, (dict, list)):
        raise NotFrozenError(val)

def _assertfrozen(val):
    if isinstance(val, (dict, list)):
        raise NotFrozenInnerError(val)
    if isinstance(val, kfrozendict):
        for ival in val.values():
            _assertfrozen(ival)
    elif isinstance(val, tuple):
        for ival in val:
            _assertfrozen(ival)
    else:
        # at this point, the value should at least be hashable
        hash(val)
        return val

def kassertfrozen(func):
    # return func
    def inner(*args, **kwargs):
        response = func(*args, **kwargs)
        # assertfrozen(response)
        return response
    return inner
