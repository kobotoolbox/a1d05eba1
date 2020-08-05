from .xlsform_translations import XlsformTranslations
from .xlsform_aliases import XlsformRenames
from .remove_empty_rows import RemoveEmpties
from .xlsform_metas_to_settings import MetasToSurveyRoot
from .choices_by_list_name import ChoicesByListName
from .xlsform_replace_truthy_strings import ReplaceTruthyStrings

from .transformer import Transformer
from .transformer_list import TransformerList


class Formpack(TransformerList):
    transformers = (
        ChoicesByListName,    # 'list name' becomes 'list_name'
        RemoveEmpties,        # rows without required columns get removed
        MetasToSurveyRoot,
        XlsformTranslations,
        XlsformRenames,
        ReplaceTruthyStrings,
    )
