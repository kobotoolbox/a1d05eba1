from .content import Content
from .content import BaseContent
from .content_variations import VARIATIONS

from .transformations.transformer import Transformer

from .utils.kfrozendict import kfrozendict, unfreeze, deepfreeze
from .utils.validate import jsonschema_validate
from .exceptions import ContentValidationError
from .build_schema import MAIN_JSONSCHEMA

def validate(content):
    jsonschema_validate(content, MAIN_JSONSCHEMA)

def full_validate(content):
    Content(content, validate=True)
