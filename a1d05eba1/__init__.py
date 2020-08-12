from .content import Content
from .transformations.transformer import Transformer
from .utils.kfrozendict import kfrozendict, unfreeze

from .content_variations import VARIATIONS

from jsonschema import validate as jsonschema_validate
from jsonschema.exceptions import ValidationError

from .build_schema import MAIN_JSONSCHEMA

def validate(content):
    Content(content, validate=True)
