import re

from jsonschema import validate, TypeChecker, Draft7Validator
from jsonschema.exceptions import ValidationError

from .kfrozendict import kfrozendict
from ..exceptions import ContentValidationError


class WIPContentValidationError(ContentValidationError):
    '''
    {schema_path}:
    '{path}' should be {schema}
    - {instance}
    '''

class ImmutableFriendlyValidator(Draft7Validator):
    def is_type(self, value, _type):
        if _type == 'object' and isinstance(value, kfrozendict):
            return True
        if _type == 'array' and isinstance(value, tuple):
            return True
        return super().is_type(value, _type)

def _spath(path):
    path = tuple(path)
    items = []
    for (index, item) in enumerate(path):
        if isinstance(item, int):
            items.append(f'[{item}]')
        else:
            items.append(f'{item}')
    return re.sub('\.\[', '[', '.'.join(items))

def jsonschema_validate(content, schema):
    try:
        validate(content, schema, cls=ImmutableFriendlyValidator)
    except ValidationError as error:
        raise error
        # validator = error.validator # e.g. 'required'
        # value = error.validator_value # e.g. ['$anchor']
        # schema = error.schema # full jsonschema
        # path = _spath(error.path) # e.g. 'survey', 0
        # schema_path = _spath(error.schema_path)
        # instance = error.instance # e.g. the row with the missing field
        # if isinstance(instance, kfrozendict):
        #     instance = instance.unfreeze()
        # raise WIPContentValidationError(**locals())
