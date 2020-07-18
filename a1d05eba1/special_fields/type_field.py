from ..schema_properties import GROUPABLE_TYPES

class TypeField:
    def __init__(self, content, typestring):
        self.key = 'type'
        self.val = typestring
        if typestring in GROUPABLE_TYPES:
            self.flat_val = 'begin_%s' % self.val
