from .kobo_rename_kuid_to_anchor import RenameKuidToAnchor
from .xlsform_replace_truthy_strings import ReplaceTruthyStrings
from .v1_renames import V1Renames

from .transformer import Transformer
from .transformer_list import TransformerList

class EnsureTranslationList(Transformer):
    def rw(self, content):
        if 'translations' not in content:
            return content.copy_in(translations=[None])
        return content


class RemoveTranslated(Transformer):
    def rw(self, content):
        if 'translated' not in content:
            return content
        (content, translated) = content.popout('translated')
        return content


class KoboXlsform(TransformerList):
    transformers = (
        RemoveTranslated,
        RenameKuidToAnchor,
        ReplaceTruthyStrings,
        V1Renames,
        EnsureTranslationList,
    )
