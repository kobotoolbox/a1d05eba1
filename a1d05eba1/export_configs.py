from .transformations import TransformerList

from .transformations import (
    ChoicesToListFW,
    DumpExtraneousAnchorsFW,
    RemoveTranslatedFromRootFW,
    RenameKuidToAnchor,
    ReplaceTruthyStrings,
    SettingsChoicesToListFW,
    XlsformRenames,
    XlsformTranslations,
)


class ExportConfigs(TransformerList):
    schema = '2'
    flat = False
    immutable = False
    remove_nulls = False
    transformers = ()
    default_settings = ()

    def __init__(self, **kwargs):
        for key in list(kwargs):
            if hasattr(self, key):
                val = kwargs.pop(key)
                setattr(self, key, val)
        super().__init__(**kwargs)

    def fw(self, content, **kwargs):
        return self._apply_transformers(content, direction='fw', **kwargs)

class DefaultExportConfigs(ExportConfigs):
    schema = '2'
    flat = False

class DefaultExportConfigsSchema1(ExportConfigs):
    schema = '1'
    flat = True
    transformers = (
        SettingsChoicesToListFW,
    )

class XlsformExport(ExportConfigs):
    schema = '1'
    flat = True
    transformers = (
        ReplaceTruthyStrings,
        DumpExtraneousAnchorsFW,
        XlsformRenames,
        XlsformTranslations,
        RemoveTranslatedFromRootFW,
        SettingsChoicesToListFW,
    )


class KoboXlsformExport(ExportConfigs):
    schema = '1'
    flat = True
    transformers = (
        ReplaceTruthyStrings,
        RenameKuidToAnchor,
        ChoicesToListFW,
    )
