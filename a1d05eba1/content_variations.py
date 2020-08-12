from jsonschema import validate as jsonschema_validate
from jsonschema.exceptions import ValidationError

from .content import Content
from .utils.yparse import yload_file as yload
from .build_schema import MAIN_JSONSCHEMA

from .utils.kfrozendict import unfreeze

from .transformations import AnchorsFromNameOrRandom
from .transformations import XlsformTranslations
from .transformations import XlsformRenames
from .transformations import RemoveEmptiesRW
from .transformations import MetasToSurveyRootRW
from .transformations import ChoicesByListNameRW
from .transformations import ReplaceTruthyStrings
from .transformations import V1RenamesRW
from .transformations import EnsureTranslationListRW
from .transformations import RenameKuidToAnchor
from .transformations import UnwrapSettingsFromListRW
from .transformations import XlsformChoicesRW


def load_input_schema(cname):
    return yload(f'input_schemas/{cname}')

VARIATIONS = {}
def _register_variation(kls):
    if kls.input_schema is None:
        raise ValueError('Needs input_schema specified')
    klsname = kls.__name__
    VARIATIONS[klsname] = kls


class X_Content(Content):
    schema_string = '1'
    input_schema = load_input_schema('X_Content')
    transformers = (
        ChoicesByListNameRW,
        RemoveEmptiesRW,
        MetasToSurveyRootRW,
        XlsformTranslations,
        XlsformRenames,
        V1RenamesRW,
        ReplaceTruthyStrings,
        UnwrapSettingsFromListRW,
        AnchorsFromNameOrRandom,
    )
_register_variation(X_Content)


class V1_Kuid_Content(Content):
    schema_string = '1'
    input_schema = load_input_schema('V1_Kuid_Content')

    transformers = (
        UnwrapSettingsFromListRW,
        RemoveEmptiesRW,
        XlsformChoicesRW,
        RenameKuidToAnchor,
        AnchorsFromNameOrRandom,
        ReplaceTruthyStrings,
        V1RenamesRW,
        EnsureTranslationListRW,
    )
_register_variation(V1_Kuid_Content)


class V1_Content_Anchors(Content):
    schema_string = '1'
    input_schema = load_input_schema('V1_Content_Anchors')
    transformers = (
        UnwrapSettingsFromListRW,
        XlsformChoicesRW,
    )
_register_variation(V1_Content_Anchors)

class V1_Content_NoAnchors(Content):
    schema_string = '1'
    input_schema = load_input_schema('V1_Content_NoAnchors')
    transformers = (
        UnwrapSettingsFromListRW,
        XlsformChoicesRW,
        AnchorsFromNameOrRandom,
    )
_register_variation(V1_Content_NoAnchors)

class V2_Content(Content):
    schema_string = '2'
    input_schema = MAIN_JSONSCHEMA
    transformers = ()

_register_variation(V2_Content)


def build_content(content, **kwargs):
    content = unfreeze(content)
    for kls in VARIATIONS.values():
        try:
            jsonschema_validate(content, kls.input_schema)
            return kls(content, **kwargs)
        except ValidationError:
            continue
    # no alt schema recognized, falling back to validation errors on main schema
    jsonschema_validate(content, MAIN_JSONSCHEMA)

def get_klass(schema_code):
    return VARIATIONS[schema_code]
