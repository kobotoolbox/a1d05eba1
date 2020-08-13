from jsonschema.exceptions import ValidationError

from .content import Content
from .utils.yparse import yload_file as yload
from .build_schema import MAIN_JSONSCHEMA

from .utils.validate import jsonschema_validate

from .exceptions import ContentValidationError

from .transformations import (
    AnchorsFromNameOrRandom,
    RenameKuidToAnchor,
    ReplaceTruthyStrings,
    XlsformRenames,
    XlsformTranslations,
    ChoicesByListNameRW,
    EnsureTranslationListRW,
    MetasToSurveyRootRW,
    RemoveEmptiesRW,
    UnwrapSettingsFromListRW,
    V1RenamesRW,
    XlsformChoicesRW,
)


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
    classname = kwargs.pop('classname', None)
    if classname:
        kls = VARIATIONS[classname]
        return kls(content, **kwargs)

    for kls in VARIATIONS.values():
        try:
            jsonschema_validate(content, kls.input_schema)
            return kls(content, **kwargs)
        except (ContentValidationError, ValidationError):
            continue
    # no alt schema recognized, falling back to validation errors on main schema
    jsonschema_validate(content, MAIN_JSONSCHEMA)

def get_klass(schema_code):
    return VARIATIONS[schema_code]
