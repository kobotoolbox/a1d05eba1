from .content import Content
from .transformations.transformer import Transformer
from .utils.kfrozendict import kfrozendict

def validate(content):
    Content(content, validate=True)
