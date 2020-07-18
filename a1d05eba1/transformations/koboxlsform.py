from . import kobo_rename_kuid_to_anchor

from .transformer import TransformerList

TRANSFORMER = TransformerList([
    kobo_rename_kuid_to_anchor,
])
