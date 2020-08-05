from .xlsform_translations import XlsformTranslations
from .xlsform_aliases import XlsformRenames
from .remove_empty_rows import RemoveEmpties
from .xlsform_metas_to_settings import MetasToSurveyRoot
from .v1_renames import V1Renames
from .choices_by_list_name import ChoicesByListName

from .anchors_when_needed import EnsureAnchorsWhenNeeded
from .anchors_when_needed import DumpExtraneousAnchors

from .transformer import Transformer

from .transformer_list import TransformerList
from .xlsform_replace_truthy_strings import ReplaceTruthyStrings


class RemoveTranslatedFromRoot(Transformer):
    def fw(self, content):
        if 'translated' in content:
            (content, translated) = content.popout('translated')
        return content


class Xlsform(TransformerList):
    name = 'XLSForm'

    transformers = (
        RemoveTranslatedFromRoot,
        ChoicesByListName,
        RemoveEmpties,

        MetasToSurveyRoot,
        XlsformTranslations,

        XlsformRenames,
        # EnsureAnchorsWhenNeeded,
        DumpExtraneousAnchors,
        V1Renames,

        ReplaceTruthyStrings,
    )
