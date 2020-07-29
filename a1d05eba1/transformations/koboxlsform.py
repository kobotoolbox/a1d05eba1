from . import kobo_rename_kuid_to_anchor
from . import xlsform_add_anchors

from .transformer import TransformerList, Transformer

class EnsureTranslationList(Transformer):
    def rw(self, content):
        if 'translations' not in content:
            return content.copy_in(translations=[None])
        return content

TRANSFORMER = TransformerList([
    kobo_rename_kuid_to_anchor,
    xlsform_add_anchors,
    EnsureTranslationList(),
], name='koboxlsform')
